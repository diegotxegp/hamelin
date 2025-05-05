# src/utils/ui_converter.py
import os
import subprocess

def convert_ui_files(ui_folder: str = "src/ui", output_folder: str = "src/windows"):
    """
    Convert all .ui files in the specified ui_folder and save them
    as Python modules in the output_folder using pyside6-uic.
    """
    # Make sure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(ui_folder):
        if filename.endswith(".ui"):
            ui_path = os.path.join(ui_folder, filename)

            # Extract the name without extension and create the output file name
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_ui.py"
            output_path = os.path.join(output_folder, output_filename)

            # Compile only if the .ui file is newer than the .py
            if not os.path.exists(output_path) or os.path.getmtime(ui_path) > os.path.getmtime(output_path):
                try:
                    print(f"⏳ Compiling: {filename}")
                    subprocess.run(
                        ["pyside6-uic", ui_path, "-o", output_path],
                        check=True
                    )
                    print(f"✅ Saved to: {output_path}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error compiling {filename}: {e}")
            else:
                print(f"⏩ Already up-to-date: {output_filename}")
