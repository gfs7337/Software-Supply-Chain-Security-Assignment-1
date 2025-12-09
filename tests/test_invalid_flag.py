import subprocess


def test_invalid_flag():
    result = subprocess.run(
        ["trufflehog", "--invalid"], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "arguments are required" in result.stderr.lower()
