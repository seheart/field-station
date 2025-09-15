# Field Station - Automated QA Framework

Tired of catching little errors manually? This QA framework automatically tests Field Station for bugs, UI issues, and regressions.

## 🚀 Quick Start

### Run All Tests
```bash
./run_qa.sh
```

### Pre-Commit Testing
```bash
python3 pre_commit_qa.py
```

## 📋 What Gets Tested

### ✅ Core Functionality
- Game initialization without crashes
- Menu navigation between all pages
- Farm setup form validation and flow
- Input handling (keyboard/mouse events)
- UI rendering without errors
- Button interactions and click detection
- Error handling for invalid inputs

### 🔍 Specific Test Cases
1. **Game Initialization**: Tests game starts properly with all required attributes
2. **Menu Navigation**: Tests all menu states render without errors
3. **Farm Setup Flow**: Tests form validation and user flow
4. **Input Handling**: Tests keyboard events (ESC, Enter) don't cause crashes
5. **UI Rendering**: Tests UI framework creates proper elements and click areas
6. **Button Interactions**: Tests button states and click detection
7. **Error Handling**: Tests edge cases like long names, special characters

## 📊 Test Report Format

```
🔍 Field Station - Automated QA Testing
======================================
🚀 Starting Field Station QA Test Suite
==================================================
✅ PASS Game Initialization (0.50s)
✅ PASS Menu Navigation (0.22s)
✅ PASS Farm Setup Flow (0.00s)
✅ PASS Input Handling (0.00s)
✅ PASS UI Rendering (0.01s)
✅ PASS Button Interactions (0.01s)
✅ PASS Error Handling (0.02s)

==================================================
📊 FIELD STATION QA TEST REPORT
==================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%
Total Execution Time: 0.76s
```

## 🛠️ Integration Options

### Option 1: Manual Testing
Run `./run_qa.sh` before making changes or commits.

### Option 2: Pre-Commit Hook
```bash
# Set up git pre-commit hook (optional)
cp pre_commit_qa.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Option 3: CI/CD Integration
Add to your CI pipeline:
```yaml
- name: Run QA Tests
  run: ./run_qa.sh
```

## 🔧 Adding New Tests

To add a new test to the framework:

1. Add a new test method to `QATestFramework` class in `test_framework.py`
2. Follow the pattern:
```python
def test_your_feature(self):
    """Test description"""
    if not self.game:
        self.add_result("Your Test", False, "Game not initialized")
        return
        
    start_time = time.time()
    try:
        # Your test code here
        assert some_condition, "Error message"
        
        self.add_result("Your Test", True, execution_time=time.time() - start_time)
    except Exception as e:
        self.add_result("Your Test", False, str(e), time.time() - start_time)
```

3. Call your test method in `run_all_tests()`

## 🐛 Common Issues Caught

- **Emoji rendering errors**: Catches pygame font issues with unicode characters
- **Missing methods**: Detects when refactoring breaks method calls
- **Input handling crashes**: Finds keyboard event handling bugs
- **UI framework errors**: Catches panel creation and rendering issues
- **Button click detection**: Finds missing click rectangles
- **Form validation bugs**: Tests edge cases in user input

## 💡 Benefits

- **Catches issues before you see them**: Automated testing runs faster than manual testing
- **Prevents regressions**: Ensures old bugs don't come back
- **Consistent testing**: Same tests run every time, no human error
- **Fast feedback**: Full test suite runs in under 1 second
- **Detailed reporting**: Shows exactly what passed/failed and execution times

## 🎯 Exit Codes

- `0`: All tests passed
- `1`: Some tests failed
- `2`: Critical framework error

Perfect for integration with build systems and CI/CD pipelines!