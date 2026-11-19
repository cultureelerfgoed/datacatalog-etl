#!/bin/sh

current_branch=$(git symbolic-ref --short head)
echo "you are on $current_branch, running tests.."


# check if virtual environment is available
if [ -d ".venv" ]; then
  echo "directory .venv exists."
else
  if ! "$PYTHON_CMD" -m venv --help &> /dev/null; then
      echo "Error: The 'venv' module is not installed in Python, please install venv: pip install venv." >&2
      return 1
  fi
  python -m venv .venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "msys" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# show which executable is being used
echo "using python executable:"
which python
# install requirements
pip install -r requirements.txt
# Run tests
python -m pytest tests/

# Retrieve exit code
test_exit_code=$?

if [[ $current_branch = "main" ]] && [ $test_exit_code -ne 0 ]; then
  echo -e "On main branch tests must pass. Aborting commit: Test failed."
  exit $is_test_passed
else
  if [ $test_exit_code -ne 0 ]; then
    echo -e "Allowing commit on non-main branch: Test failed."
  else
    echo -e "Allowing commit: All tests passed."
  fi
fi

