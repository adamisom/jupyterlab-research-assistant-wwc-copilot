#!/bin/bash
# Run pytest with test_release excluded from PATH
# This prevents pytest from using the wrong Python interpreter

# Remove test_release from PATH
CLEAN_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v test_release | tr '\n' ':' | sed 's/:$//')
export PATH="$CLEAN_PATH"

# Find python3 that has pytest (try common locations)
if command -v python3 >/dev/null 2>&1 && python3 -m pytest --version >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif [ -f "venv/bin/python3" ] && venv/bin/python3 -m pytest --version >/dev/null 2>&1; then
    PYTHON_CMD=venv/bin/python3
elif [ -f ".venv/bin/python3" ] && .venv/bin/python3 -m pytest --version >/dev/null 2>&1; then
    PYTHON_CMD=.venv/bin/python3
else
    echo "Error: Could not find python3 with pytest installed"
    exit 1
fi

# Run pytest
$PYTHON_CMD -m pytest jupyterlab_research_assistant_wwc_copilot/tests/ -v --ignore=test_release "$@"

