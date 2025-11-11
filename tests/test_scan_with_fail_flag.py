import subprocess

def test_scan_with_fail_flag():
    result = subprocess.run(["trufflehog", "git", "file://.", "--no-verification", "--since-commit", "HEAD", "--fail"], capture_output=True, text=True)
    assert result.returncode in [0, 1]
