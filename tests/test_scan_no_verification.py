import subprocess


def test_scan_no_verification():
    result = subprocess.run(
        [
            "trufflehog",
            "git",
            "file://.",
            "--no-verification",
            "--since-commit",
            "HEAD",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode in [0, 1]
