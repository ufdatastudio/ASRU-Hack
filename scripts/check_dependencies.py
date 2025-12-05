"""
Check if all required dependencies are installed for model downloading.
"""
import sys
import importlib

REQUIRED_PACKAGES = {
    'torch': 'torch',
    'transformers': 'transformers',
    'soundfile': 'soundfile',
    'numpy': 'numpy',
}

OPTIONAL_PACKAGES = {
    'audio_flamingo': 'audio-flamingo (required for AF3)',
}

def check_package(package_name, display_name=None):
    """Check if a package is installed."""
    if display_name is None:
        display_name = package_name
    
    try:
        importlib.import_module(package_name)
        print(f"✓ {display_name}")
        return True
    except ImportError:
        print(f"✗ {display_name} - NOT INSTALLED")
        return False

def main():
    print("=" * 60)
    print("Checking Dependencies for African Health Studio")
    print("=" * 60)
    print()
    
    print("Required packages:")
    all_required = True
    for package, display in REQUIRED_PACKAGES.items():
        if not check_package(package, display):
            all_required = False
    
    print()
    print("Optional packages:")
    for package, display in OPTIONAL_PACKAGES.items():
        check_package(package, display)
    
    print()
    print("=" * 60)
    
    if not all_required:
        print("Missing required packages!")
        print()
        print("Install missing packages with UV:")
        print("  uv pip install <package-name>")
        print()
        print("Or add to pyproject.toml and run:")
        print("  uv sync")
        sys.exit(1)
    else:
        print("All required packages are installed!")
        print()
        print("You can now run: bash scripts/download_models.sh")
        sys.exit(0)

if __name__ == "__main__":
    main()

