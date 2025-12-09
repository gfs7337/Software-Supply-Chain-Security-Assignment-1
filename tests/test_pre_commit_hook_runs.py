import subprocess


def test_pre_commit_hook_runs():
    result = subprocess.run(
        ["pre-commit", "run", "--all-files"], capture_output=True, text=True
    )
    assert "TruffleHog" in result.stdout or "trufflehog" in result.stdout
