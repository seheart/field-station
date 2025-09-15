#!/usr/bin/env python3
"""
Pre-commit QA Hook for Field Station
Runs before each commit to catch issues early
"""

import subprocess
import sys
import os

def run_qa_tests():
    """Run the QA test suite"""
    print("🔍 Running pre-commit QA tests...")
    
    # Change to the field_station directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run the QA test suite
        result = subprocess.run(['python3', 'test_framework.py'], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("❌ QA tests timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running QA tests: {e}")
        return False

def run_syntax_check():
    """Run basic Python syntax checking"""
    print("🔍 Checking Python syntax...")
    
    python_files = ['field_station.py', 'ui_framework.py', 'menu_icons.py']
    
    for file in python_files:
        if os.path.exists(file):
            try:
                result = subprocess.run(['python3', '-m', 'py_compile', file],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Syntax error in {file}:")
                    print(result.stderr)
                    return False
            except Exception as e:
                print(f"❌ Error checking {file}: {e}")
                return False
    
    print("✅ All Python files have valid syntax")
    return True

def main():
    """Main pre-commit check"""
    print("🚀 Field Station Pre-Commit QA Check")
    print("=" * 40)
    
    # Run syntax check first (fast)
    if not run_syntax_check():
        print("💥 Pre-commit FAILED: Syntax errors detected")
        return 1
    
    # Run comprehensive QA tests
    if not run_qa_tests():
        print("💥 Pre-commit FAILED: QA tests failed")
        return 1
    
    print("=" * 40)
    print("✅ Pre-commit QA checks PASSED!")
    print("   Safe to commit your changes.")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)