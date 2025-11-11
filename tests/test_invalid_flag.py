import subprocess

def test_invalid_flag():
    result = subprocess.run(["trufflehog", "--invalid"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "unknown flag" in result.stderr.lower()
