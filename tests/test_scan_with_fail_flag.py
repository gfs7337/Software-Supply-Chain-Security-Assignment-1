import subprocess


def test_missing_repo_path():
    result = subprocess.run(
        ["trufflehog", "git"], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "fatal: repository 'git' does not exist" in result.stderr.lower()
