#!/usr/bin/env python3
"""
Simple test to check if our files have the right structure for uv.
This doesn't actually run uv, but checks the configuration.
"""

import json
import tomllib
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if a file exists."""
    if filepath.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def test_toml_valid(filepath, description):
    """Test if a TOML file is valid."""
    try:
        with open(filepath, 'rb') as f:
            data = tomllib.load(f)
        print(f"✅ {description} is valid TOML")
        return True, data
    except Exception as e:
        print(f"❌ {description} has TOML error: {e}")
        return False, None

def main():
    """Run configuration tests."""
    print("🧪 Testing Political Strategy Game uv configuration...")
    print("=" * 60)
    
    # Project directory is the parent of the validation directory
    project_dir = Path(__file__).parent.parent
    all_tests_passed = True
    
    # Test 1: Required files exist
    print("\n📁 Testing file existence...")
    required_files = [
        (project_dir / "pyproject.toml", "pyproject.toml"),
        (project_dir / "uv.toml", "uv.toml"),
        (project_dir / "demos" / "demo.py", "demos/demo.py"),
        (project_dir / "src" / "__init__.py", "src/__init__.py"),
        (project_dir / "src" / "core" / "__init__.py", "src/core/__init__.py"),
        (project_dir / "src" / "core" / "advisor.py", "src/core/advisor.py"),
    ]
    
    for filepath, description in required_files:
        if not test_file_exists(filepath, description):
            all_tests_passed = False
    
    # Test 2: TOML files are valid
    print("\n📄 Testing TOML file validity...")
    
    # Test pyproject.toml
    pyproject_valid, pyproject_data = test_toml_valid(project_dir / "pyproject.toml", "pyproject.toml")
    if not pyproject_valid:
        all_tests_passed = False
    
    # Test uv.toml  
    uv_toml_valid, uv_data = test_toml_valid(project_dir / "uv.toml", "uv.toml")
    if not uv_toml_valid:
        all_tests_passed = False
    
    # Test 3: pyproject.toml structure
    if pyproject_valid and pyproject_data:
        print("\n⚙️  Testing pyproject.toml structure...")
        
        if "project" in pyproject_data:
            print("✅ [project] section found")
            
            project = pyproject_data["project"]
            if "name" in project:
                print(f"✅ Project name: {project['name']}")
            else:
                print("❌ Project name missing")
                all_tests_passed = False
                
            if "dependencies" in project:
                print(f"✅ Dependencies defined: {len(project['dependencies'])} items")
            else:
                print("❌ Dependencies missing")
                all_tests_passed = False
                
            if "requires-python" in project:
                print(f"✅ Python requirement: {project['requires-python']}")
            else:
                print("❌ Python requirement missing")
                all_tests_passed = False
        else:
            print("❌ [project] section missing")
            all_tests_passed = False
            
        if "build-system" in pyproject_data:
            print("✅ [build-system] section found")
        else:
            print("❌ [build-system] section missing")
            all_tests_passed = False
    
    # Test 4: uv.toml structure  
    if uv_toml_valid and uv_data:
        print("\n⚙️  Testing uv.toml structure...")
        
        # Check that there's no [tool.uv] section (which would be wrong)
        if "tool" in uv_data:
            print("❌ uv.toml should not contain [tool.*] sections")
            all_tests_passed = False
        else:
            print("✅ uv.toml has correct top-level structure")
    
    # Test 5: Demo script structure
    print("\n🐍 Testing demo.py structure...")
    demo_path = project_dir / "demos" / "demo.py"
    if demo_path.exists():
        with open(demo_path, 'r') as f:
            demo_content = f.read()
        
        if "def main():" in demo_content:
            print("✅ main() function found in demo.py")
        else:
            print("❌ main() function missing in demo.py")
            all_tests_passed = False
            
        if "sys.path.insert" in demo_content:
            print("✅ Path manipulation found (good for standalone execution)")
        else:
            print("⚠️  No path manipulation found")
            
        if "from src.core.advisor import" in demo_content or "from core.advisor import" in demo_content:
            print("✅ Core module imports found")
        else:
            print("❌ Core module imports missing")
            all_tests_passed = False
    
    # Summary
    print(f"\n🎯 Test Summary:")
    if all_tests_passed:
        print("✅ All configuration tests PASSED!")
        print("🚀 The setup should work with uv now.")
        print("\nNext steps:")
        print("   1. Run: uv venv")
        print("   2. Run: uv pip install -e \".[dev]\"")
        print("   3. Run: uv run python demo.py")
    else:
        print("❌ Some tests FAILED!")
        print("🔧 Please fix the issues above before using uv.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
