"""Test `taste_soup` script."""
import subprocess
import os


def test_installation():
    """Check installation."""
    complete_process = subprocess.run(
        [
            "taste_soup",
            "-h",
        ],
        check=False,
    )
    assert complete_process.returncode == os.EX_OK


def test_invalid_solution():
    """Check if taste reports invalid solution."""
    complete_process = subprocess.run(
        [
            "taste_soup",
            "tests/integration/data/invalid_solution.yaml",
        ],
        check=False,
    )
    assert complete_process.returncode == os.EX_DATAERR


def test_valid_solution():
    """Check if taste reports valid solution."""
    complete_process = subprocess.run(
        [
            "taste_soup",
            "tests/integration/data/valid_solution.yaml",
        ],
        check=False,
    )
    assert complete_process.returncode == os.EX_OK
