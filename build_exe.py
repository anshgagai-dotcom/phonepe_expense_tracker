"""
Automated Build Script for Packaging PhonePe Expense Tracker into a Single-File .exe
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build():
    print("=" * 60)
    print(" BUILDING PHONEPE EXPENSE TRACKER STANDALONE .EXE ")
    print("=" * 60)

    # 1. Ensure app icon exists
    icon_path = BASE_DIR / "frontend" / "assets" / "icons" / "app_icon.ico"
    if not icon_path.exists():
        print(f"Creating .ico icon from logo...")
        from PIL import Image
        logo_png = BASE_DIR / "frontend" / "assets" / "icons" / "phonepe_logo.png"
        img = Image.open(logo_png)
        img.save(icon_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(f"Icon generated at: {icon_path}")

    # 2. Prepare PyInstaller command
    frontend_dir = BASE_DIR / "frontend"
    data_dir = BASE_DIR / "data"
    entrypoint = BASE_DIR / "desktop_app.py"
    output_name = "PhonePe_Expense_Tracker"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--noconsole",
        f"--name={output_name}",
        f"--icon={str(icon_path)}",
        f"--add-data={str(frontend_dir)};frontend",
        f"--add-data={str(data_dir)};data",
        "--hidden-import=webview",
        "--hidden-import=bottle",
        "--hidden-import=clr",
        "--hidden-import=pythonnet",
        str(entrypoint)
    ]

    print("\nExecuting PyInstaller command:")
    print(" ".join(cmd))
    print("-" * 60)

    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    if result.returncode != 0:
        print("\n[ERROR] PyInstaller build failed!")
        sys.exit(result.returncode)

    dist_exe = BASE_DIR / "dist" / f"{output_name}.exe"
    if dist_exe.exists():
        size_mb = dist_exe.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print(" [SUCCESS] EXECUTABLE BUILT SUCCESSFULLY! ")
        print(f" Location : {dist_exe}")
        print(f" Size     : {size_mb:.2f} MB")
        print("=" * 60 + "\n")
        print("You can now distribute this single .exe file to any Windows machine!")
    else:
        print(f"\n[ERROR] Expected executable not found at: {dist_exe}")
        sys.exit(1)

if __name__ == "__main__":
    build()
