#!/bin/bash
# Local test runner script for farming game

set -e

echo "🚜 Farming Game - Local Test Suite"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if we're in the right directory
if [[ ! -f "farming_game.py" ]]; then
    print_status $RED "❌ Error: farming_game.py not found. Run this script from the game directory."
    exit 1
fi

# 1. Syntax Check
print_status $YELLOW "🔍 Running syntax check..."
if python3 -m py_compile farming_game.py; then
    print_status $GREEN "✅ Syntax check passed"
else
    print_status $RED "❌ Syntax check failed"
    exit 1
fi

# 2. Code Style Check (if black is available)
if command -v black &> /dev/null; then
    print_status $YELLOW "🎨 Checking code style..."
    if black --check --line-length=100 *.py; then
        print_status $GREEN "✅ Code style check passed"
    else
        print_status $YELLOW "⚠️  Code style issues found (run 'black --line-length=100 *.py' to fix)"
    fi
else
    print_status $YELLOW "ℹ️  Skipping style check (black not installed)"
fi

# 3. Linting (if flake8 is available)
if command -v flake8 &> /dev/null; then
    print_status $YELLOW "🔎 Running linter..."
    if flake8 --max-line-length=100 --ignore=E203,W503 *.py; then
        print_status $GREEN "✅ Linting passed"
    else
        print_status $YELLOW "⚠️  Linting issues found"
    fi
else
    print_status $YELLOW "ℹ️  Skipping lint check (flake8 not installed)"
fi

# 4. Unit Tests
print_status $YELLOW "🧪 Running unit tests..."
if python3 test_farming_game.py; then
    print_status $GREEN "✅ Unit tests passed"
else
    print_status $RED "❌ Unit tests failed"
    exit 1
fi

# 5. Game Launch Test
print_status $YELLOW "🎮 Testing game launch..."
timeout 3s python3 farming_game.py > /dev/null 2>&1 || true
if [[ $? -eq 124 ]]; then
    print_status $GREEN "✅ Game launches successfully (timed out as expected)"
else
    print_status $YELLOW "⚠️  Game may have crashed on startup"
fi

# 6. File Structure Check
print_status $YELLOW "📁 Checking file structure..."
required_files=("farming_game.py" "test_farming_game.py" "game_data.html")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    print_status $GREEN "✅ All required files present"
else
    print_status $YELLOW "⚠️  Missing files: ${missing_files[*]}"
fi

# Summary
echo ""
print_status $GREEN "🎯 Test Summary Complete!"
echo ""
echo "To install testing dependencies:"
echo "  pip install black flake8 pytest pytest-cov mypy"
echo ""
echo "To run specific checks:"
echo "  Syntax: python3 -m py_compile farming_game.py"
echo "  Style:  black --line-length=100 *.py"
echo "  Lint:   flake8 --max-line-length=100 *.py"
echo "  Tests:  python3 test_farming_game.py"
echo ""