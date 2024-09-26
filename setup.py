import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "PyQt5"],
    "excludes": ["tkinter"],
    "include_files": [
        "main_ui.py",
        "importfunctions.py",
        "main.spec",
        ("data", "data")
    ]
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="CCSorter",
    version="1.0",
    description="CC Sorter and Storeage with API Callback Functions",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)