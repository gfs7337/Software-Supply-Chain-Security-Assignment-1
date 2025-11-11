import subprocess

def test_missing_repo_path():
    result = subprocess.run(["trufflehog", "git"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "requires at least 1 arg(s)" in result.stderr.lower()
