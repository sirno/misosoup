"""Integration tests for misosoup."""

import subprocess

import yaml


def test_installation():
    """Check installation."""
    complete_process = subprocess.run(
        [
            "misosoup",
            "-h",
        ],
        check=False,
    )
    assert complete_process.returncode == 0


def test_integration():
    """Run example problem."""
    complete_process = subprocess.run(
        [
            "misosoup",
            "--media",
            "tests/data/medium.yaml",
            "--strain",
            "A1R12",
            "--parsimony",
            "tests/data/A1R12.xml",
            "tests/data/I2R16.xml",
        ],
        capture_output=True,
        check=False,
    )
    assert complete_process.returncode == 0
    # print(complete_process.stdout)
    out = yaml.safe_load(complete_process.stdout.decode("utf8"))
    print(out)
    assert out["ac"]["A1R12"][0]["community"]["y_A1R12"] == 1
    assert out["ac"]["A1R12"][0]["community"]["y_I2R16"] == 1
