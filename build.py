"""
Build script for creating standalone .exe
Usage: python build.py
"""
import os
import subprocess
import sys


def build_exe():
    """Build standalone executable using PyInstaller"""
    
    print("=" * 60)
    print("Building MLBevo Log Viewer executable")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\n[ERROR] PyInstaller not found!")
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[SUCCESS] PyInstaller installed successfully\n")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",              # Single executable
        "--windowed",             # No console window
        "--name=MLBevo_LogViewer", # Output name
        "--clean",                # Clean cache
        "main.py"
    ]
    
    # Add icon if exists
    if os.path.exists("icon.ico"):
        cmd.insert(1, "--icon=icon.ico")
    
    print("\nRunning PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Build successful!")
        print("=" * 60)
        print(f"\nExecutable location: dist\\MLBevo_LogViewer.exe")
        print(f"Size: ~{os.path.getsize('dist/MLBevo_LogViewer.exe') / (1024*1024):.1f} MB")
        print("\nYou can now distribute the .exe file independently!")
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("[ERROR] Build failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
