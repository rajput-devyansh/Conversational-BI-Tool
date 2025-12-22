import os
import shutil
from pathlib import Path

# Folders to delete
CACHE_DIRS = {
    "__pycache__",
    ".pytest_cache",
}

# File extensions to delete
CACHE_FILES = {".pyc", ".pyo"}

# Folders to SKIP entirely
SKIP_DIRS = {"venv", ".git", ".idea", ".vscode"}

def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)

def clean_project(root: Path):
    removed_dirs = 0
    removed_files = 0

    for path in root.rglob("*"):
        if should_skip(path):
            continue

        # Delete cache directories
        if path.is_dir() and path.name in CACHE_DIRS:
            shutil.rmtree(path, ignore_errors=True)
            removed_dirs += 1
            print(f"🗑️ Removed dir: {path}")

        # Delete cache files
        elif path.is_file() and path.suffix in CACHE_FILES:
            try:
                path.unlink()
                removed_files += 1
                print(f"🗑️ Removed file: {path}")
            except Exception:
                pass

    print("\n✅ Cleanup complete")
    print(f"   Directories removed: {removed_dirs}")
    print(f"   Files removed: {removed_files}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    clean_project(project_root)