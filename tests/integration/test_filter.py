"""Test `taste_soup` script."""
import subprocess
import yaml
import os


def test_installation():
    """Check installation."""
    complete_process = subprocess.run(
        [
            "filter_soup",
            "-h",
        ],
        check=False,
    )
    assert complete_process.returncode == os.EX_OK


def test_filter():
    """Check if filter removes the correct reactions."""
    complete_process = subprocess.run(
        [
            "filter_soup",
            "tests/integration/data/valid_solution.yaml",
        ],
        capture_output=True,
        check=False,
    )
    assert complete_process.returncode == os.EX_OK
    out = yaml.safe_load(complete_process.stdout)
    assert not "other" in out["ac"]["AAAA"][0]
    assert "community_growth" in out["ac"]["AAAA"][0]
    assert "R_EX_meta_e_AAAA_INT" in out["ac"]["AAAA"][0]
    assert "R_EX_meta_e_BBBB_INT" in out["ac"]["AAAA"][0]
    assert "R_EX_meta_e" in out["ac"]["AAAA"][0]
    assert "y_BBBB" in out["ac"]["AAAA"][0]
