def test_bandit_config_in_pyproject():
    with open("pyproject.toml") as f:
        content = f.read()
    assert "[tool.bandit]" in content
