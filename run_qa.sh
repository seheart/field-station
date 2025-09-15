#!/bin/bash
# Quick QA Runner for Field Station
# Run this script to automatically test for bugs and issues

echo "🔍 Field Station - Automated QA Testing"
echo "======================================"

# Set headless mode for CI/automated testing
export SDL_VIDEODRIVER=dummy

# Run the test suite
python3 test_framework.py
TEST_EXIT_CODE=$?

echo ""
echo "======================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests PASSED! Field Station is ready to go."
elif [ $TEST_EXIT_CODE -eq 1 ]; then
    echo "⚠️  Some tests FAILED. Please review the issues above."
else
    echo "💥 Critical testing error occurred."
fi

echo "======================================"
exit $TEST_EXIT_CODE