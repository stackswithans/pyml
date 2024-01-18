import expan.main as expmain
import pytest


# expand test files
expmain.main(["tests/test_pysx.pyxp", "-o", "tests/test_pysx.py"])

# run tests
pytest.main(["tests/"])
