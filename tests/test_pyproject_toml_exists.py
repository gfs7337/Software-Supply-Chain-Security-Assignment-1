import os

def test_pyproject_toml_exists():
    assert os.path.exists("pyproject.toml")
