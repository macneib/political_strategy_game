#!/usr/bin/env python3
"""Simple test to validate TOML files."""

import toml
import sys
from pathlib import Path

def test_toml_file(filepath):
    """Test if a TOML file is valid."""
    try:
        with open(filepath, 'r') as f:
            data = toml.load(f)
        print(f"✅ {filepath} is valid TOML")
        return True
    except Exception as e:
        print(f"❌ {filepath} has error: {e}")
        return False

def main():
    project_dir = Path(__file__).parent
    
    print("🧪 Testing TOML file validity...")
    
    # Test pyproject.toml
    success1 = test_toml_file(project_dir / "pyproject.toml")
    
    # Test uv.toml  
    success2 = test_toml_file(project_dir / "uv.toml")
    
    if success1 and success2:
        print("✅ All TOML files are valid!")
        return True
    else:
        print("❌ Some TOML files have errors")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
