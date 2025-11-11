import subprocess

def test_help_flag():
    result = subprocess.run(["trufflehog", "--help"], capture_output=True, text=True)
    assert "Usage" in result.stdout
