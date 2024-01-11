import expan.main as expmain
import pytest


# expand test files
expmain.main(["tests/test_pysx.pyxp", "-o", "tests/test_pysx.py"])
expmain.main(["tests/test_errors.pyxp", "-o", "tests/test_errors.py"])

# run tests
pytest.main(["tests/"])
