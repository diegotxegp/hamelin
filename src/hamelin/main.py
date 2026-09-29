"""
HAMELIN - Application Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parses arguments and launches the GUI (or CLI fallback mode).
"""

import os
import shutil
import subprocess
import sys
import argparse
from pathlib import Path


def _run_as_python_interpreter(argv):
    """In a PyInstaller build, sys.executable is this binary, not python.
    Ray (used by Ludwig for training) starts its workers, log monitor, etc.
    as `sys.executable [-u] script.py ...` or `sys.executable -m module ...`,
    so the binary has to behave like the interpreter for those calls."""
    import os
    import runpy

    while argv and argv[0].startswith("-") and argv[0] not in ("-c", "-m"):
        if argv[0] in ("-W", "-X"):
            argv = argv[1:]
        argv = argv[1:]

    if argv[0] == "-c":
        sys.argv = ["-c"] + argv[2:]
        exec(compile(argv[1], "<string>", "exec"), {"__name__": "__main__"})
    elif argv[0] == "-m":
        sys.argv = [argv[1]] + argv[2:]
        runpy.run_module(argv[1], run_name="__main__", alter_sys=True)
    else:
        sys.argv = argv
        sys.path.insert(0, os.path.dirname(os.path.abspath(argv[0])))
        runpy.run_path(argv[0], run_name="__main__")
    sys.exit(0)


if getattr(sys, "frozen", False) and len(sys.argv) > 1 and (
    sys.argv[1].endswith(".py") or sys.argv[1] in ("-c", "-m", "-u", "-S", "-s", "-E", "-B", "-I", "-W", "-X")
):
    _run_as_python_interpreter(sys.argv[1:])

import multiprocessing
multiprocessing.freeze_support()

from hamelin.utils.logger import log
from hamelin.utils.config_manager import config
from hamelin.utils.error_handler import install_global_exception_handler
from hamelin import __version__


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=f"HAMELIN v{__version__} - Clinical Research AutoML Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Run in debug mode:
    hamelin --debug

  Use custom config:
    hamelin --config /path/to/config.yaml

  Show version:
    hamelin --version
        """
    )

    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
    parser.add_argument('--config', type=str, metavar='PATH', help='Path to custom configuration file')
    parser.add_argument('--version', action='version', version=f'HAMELIN v{__version__}')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI (for testing or CLI mode)')

    return parser.parse_args()


def _disable_unsupported_gpu():
    """Hide the GPU from this process (and, via inherited env, every Ray/
    Ludwig worker subprocess) if it exists but isn't one the installed
    PyTorch build actually has kernels for.

    Ray/Ludwig auto-detect any CUDA-capable GPU and schedule training
    trials on it unconditionally - on an old/unsupported GPU (e.g. compute
    capability sm_50 when the installed torch only ships sm_75+ kernels)
    this doesn't fail until deep inside a Ray worker mid-training, as a
    cryptic ``CUBLAS_STATUS_ARCH_MISMATCH``, long after the point where a
    clean CPU fallback would have been simple. Checked once at startup, in
    throwaway subprocesses, so a CUDA context doesn't get pinned to *this*
    process before we've decided whether the GPU should be visible at all.
    """
    if "CUDA_VISIBLE_DEVICES" in os.environ:
        return  # already explicitly configured - respect it

    if shutil.which("nvidia-smi") is None:
        return  # no NVIDIA driver/GPU on this machine - nothing to check

    try:
        smi = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            timeout=5, capture_output=True, text=True,
        )
        if smi.returncode != 0 or not smi.stdout.strip():
            return
    except Exception:
        return  # no usable nvidia-smi - let torch/ray behave as normal

    # The verdict is printed rather than signalled through sys.exit(1): a
    # debugger set to break on raised exceptions pauses on that SystemExit
    # inside this throwaway subprocess, which looked like a second process
    # to close every time the app was started under it.
    probe = (
        "import torch\n"
        "verdict = 'ok'\n"
        "if torch.cuda.is_available():\n"
        "    major, minor = torch.cuda.get_device_capability(0)\n"
        "    arch = f'sm_{major}{minor}'\n"
        "    supported = torch.cuda.get_arch_list()\n"
        "    if supported and arch not in supported:\n"
        "        verdict = 'unsupported'\n"
        "print(verdict)\n"
    )
    try:
        # sys.executable [-c] is the same subprocess re-entry pattern Ray
        # itself relies on, already handled by _run_as_python_interpreter
        # above when this is a frozen build.
        probe_result = subprocess.run(
            [sys.executable, "-c", probe], timeout=30, capture_output=True,
        )
    except Exception:
        log.warning("GPU compatibility probe failed to run; leaving GPU visible")
        return

    if probe_result.returncode == 0 and b"unsupported" in probe_result.stdout:
        log.warning(
            "Detected GPU's compute capability isn't supported by the "
            "installed PyTorch build - disabling GPU for this session "
            "(training will run on CPU instead of crashing mid-run)."
        )
        os.environ["CUDA_VISIBLE_DEVICES"] = ""


def initialize_application(args):
    """Set up logging, load config, install exception handler, log startup info."""
    if args.debug:
        log.set_level('DEBUG')
        log.debug("Debug mode enabled")
    else:
        log.set_level('INFO')

    if args.config:
        custom_config_path = Path(args.config)
        if custom_config_path.exists():
            log.info(f"Loading custom configuration from: {custom_config_path}")
            # TODO: Implement custom config loading
        else:
            log.warning(f"Custom config file not found: {custom_config_path}")
            log.info("Using default configuration")

    install_global_exception_handler()
    _disable_unsupported_gpu()

    log.info("=" * 60)
    log.info(f"HAMELIN v{__version__} - Clinical Research AutoML")
    log.info("=" * 60)
    log.info(f"Python version: {sys.version}")
    log.info(f"Application path: {Path(__file__).parent}")
    log.info(f"Configuration: {config.config_file}")
    log.info(f"Debug mode: {args.debug}")
    log.info("=" * 60)


def run_gui():
    """Launch the graphical user interface (PySide6 + Fluent Widgets)."""
    log.info("Launching GUI...")

    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        from hamelin.view.main_window import MainWindow
        from hamelin.i18n import set_language

        app = QApplication(sys.argv)
        app.setApplicationName("HAMELIN")
        app.setApplicationVersion(__version__)

        # PyInstaller builds get this for free from hamelin.spec's own
        # icon=... setting (baked into the executable's resources) - set it
        # here too so the taskbar/window icon also shows up when running
        # straight from source (uv run hamelin / python -m hamelin).
        from hamelin.utils.paths import resources_dir
        logo_path = resources_dir() / "assets" / "logo.png"
        if logo_path.exists():
            app.setWindowIcon(QIcon(str(logo_path)))

        lang = config.get("app.language", "en")
        set_language(lang)
        log.debug(f"i18n initialized with language: {lang}")

        # Warning/error banners become usage-log events (usability study).
        from hamelin.utils.usage_logger import install_infobar_logging
        install_infobar_logging()

        # The app uses the plain arrow cursor everywhere; a few widgets
        # (HyperlinkButton, help buttons) ask for a pointing hand on their
        # own. Qt Style Sheets have no `cursor` property, so this needs a
        # real event filter rather than QSS.
        from hamelin.view.widgets import ArrowCursorFilter
        _cursor_filter = ArrowCursorFilter(app)
        app.installEventFilter(_cursor_filter)

        log.debug("Creating main window")
        window = MainWindow()

        log.info("GUI launched successfully")

        exit_code = app.exec()

        log.debug(f"GUI closed with exit code: {exit_code}")
        return exit_code

    except ImportError as e:
        log.error(f"Failed to import GUI dependencies: {e}")
        log.error("Please ensure PySide6 and PySide6-Fluent-Widgets are installed")
        return 1

    except Exception as e:
        log.error(f"Failed to launch GUI: {e}", exc_info=True)
        return 1


def run_cli():
    """Run in CLI mode (no GUI) - useful for testing/automated workflows."""
    log.info("Running in CLI mode (no GUI)")
    log.info("Application initialized successfully")

    print("\n" + "=" * 60)
    print(f"HAMELIN v{__version__} - CLI Mode")
    print("=" * 60)
    print(f"Configuration: {config.get('app.name')}")
    print(f"Theme: {config.get('ui.theme')}")
    print(f"Debug: {config.get('app.debug')}")
    print("=" * 60)
    print("\nNo GUI dependencies required in this mode.")
    print("Press Ctrl+C to exit...")
    print("=" * 60 + "\n")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Application shutdown requested")
        return 0


def shutdown_application():
    """Perform cleanup before application exits."""
    log.info("=" * 60)
    log.info("HAMELIN shutting down...")
    log.info("Performing cleanup...")
    log.info("Cleanup complete")
    log.info(f"HAMELIN v{__version__} shutdown successfully")
    log.info("=" * 60)


def main() -> int:
    """Parse args, initialize the app, run GUI or CLI, then clean up."""
    exit_code = 0

    try:
        args = parse_arguments()
        initialize_application(args)

        if args.no_gui:
            exit_code = run_cli()
        else:
            exit_code = run_gui()

    except KeyboardInterrupt:
        log.info("Received keyboard interrupt")
        exit_code = 0

    except Exception as e:
        log.critical(f"Fatal error: {e}", exc_info=True)
        exit_code = 1

    finally:
        shutdown_application()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
