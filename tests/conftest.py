"""Shared test setup: keep automated runs out of the real usability log."""
import pytest

from hamelin.utils.usage_logger import usage_log


@pytest.fixture(autouse=True, scope="session")
def _isolated_usage_log(tmp_path_factory):
    """usage_log appends to workspace/logs/usage_log.csv, which holds the
    usability-study data of real sessions; tests must not add rows to it."""
    original = usage_log._path
    usage_log._path = tmp_path_factory.mktemp("usage") / "usage_log.csv"
    usage_log._path.write_text(",".join(usage_log._FIELDS) + "\n", encoding="utf-8")
    yield
    usage_log._path = original


@pytest.fixture(autouse=True, scope="session")
def _isolated_config(tmp_path_factory):
    """Closing a MainWindow saves the window size to app_config.yaml; keep
    that (and any other config write) away from the user's real file."""
    from hamelin.utils.config_manager import config

    original_dir, original_file = config.config_dir, config.config_file
    config.config_dir = tmp_path_factory.mktemp("config")
    config.config_file = config.config_dir / "app_config.yaml"
    yield
    config.config_dir, config.config_file = original_dir, original_file
