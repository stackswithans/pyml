import expan.main as expmain
import pytest


# expand test file
expmain.main(["tests/test_pysx.pyxp", "-o", "tests/test_pysx.py"])

# run tests
pytest.main(["tests/test_pysx.py"])
