#!/usr/bin/env python3
"""Build script for SimpleTimerBank desktop application.

This script automates the process of building a standalone executable
using PyInstaller. It handles cleanup, building, and basic validation.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status.
    
    Parameters
    ----------
    cmd : list[str]
        Command and arguments to execute.
    description : str
        Description of what the command does.
        
    Returns
    -------
    bool
        True if command succeeded, False otherwise.
    """
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def clean_build_artifacts() -> None:
    """Remove previous build artifacts."""
    artifacts = [
        "build",
        "dist", 
        "__pycache__",
        "*.spec.bak",
    ]
    
    print("🧹 Cleaning previous build artifacts...")
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
            else:
                path.unlink()
                print(f"   Removed file: {path}")


def build_executable() -> bool:
    """Build the standalone executable using PyInstaller.
    
    Returns
    -------
    bool
        True if build succeeded, False otherwise.
    """
    # Ensure we're in the project root
    if not Path("pyinstaller.spec").exists():
        print("❌ pyinstaller.spec not found. Run this script from the project root.")
        return False
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Run PyInstaller
    cmd = ["uv", "run", "pyinstaller", "pyinstaller.spec", "--clean"]
    success = run_command(cmd, "Building executable with PyInstaller")
    
    if success:
        # Check if executable was created
        exe_path = Path("dist/SimpleTimerBank.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"🎉 Build completed successfully!")
            print(f"   Executable: {exe_path}")
            print(f"   Size: {size_mb:.1f} MB")
            return True
        else:
            print(f"❌ Build completed but executable not found at {exe_path}")
            return False
    
    return False


def main() -> int:
    """Main build function.
    
    Returns
    -------
    int
        Exit code (0 for success, 1 for failure).
    """
    print("🚀 SimpleTimerBank Build Script")
    print("=" * 40)
    
    # Verify dependencies
    if not run_command(["uv", "--version"], "Checking uv installation"):
        print("❌ uv is required but not installed. Please install uv first.")
        return 1
    
    # Build executable
    if build_executable():
        print("\n✅ Build process completed successfully!")
        print("💡 You can now run the executable from: dist/SimpleTimerBank.exe")
        return 0
    else:
        print("\n❌ Build process failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 