# src/main.py
import os
from utils.ui_converter import convert_ui_files

def main():
    # Get the current directory of the script (src)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the paths for the ui folder and the output folder relative to the script's directory
    ui_folder = os.path.join(base_dir, "..", "ui")  # Folder where the .ui files are located (one level up)
    output_folder = os.path.join(base_dir, "windows")  # Folder where the .py files will be saved

    # Make sure the paths are correct (optional)
    if not os.path.exists(ui_folder):
        print(f"❌ The UI folder '{ui_folder}' does not exist. Please check the path.")
        return

    # Call the conversion function
    convert_ui_files(ui_folder, output_folder)

if __name__ == "__main__":
    main()
