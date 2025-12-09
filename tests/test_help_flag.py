import subprocess  # <-- This line is required to fix the NameError

# ... other imports if any ...


def test_help_flag():
    result = subprocess.run(
        ["trufflehog", "--help"], capture_output=True, text=True
    )
    # ... rest of the test assertion ...
