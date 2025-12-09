import subprocess


def test_version_flag():
    result = subprocess.run(
        ["trufflehog", "--version"], capture_output=True, text=True
    )
    assert "trufflehog" in result.stdout.lower()
