"""Integration tests."""

import subprocess
import yaml


def test_installation():
    """Build and run docker container."""
    subprocess.run(
        ["docker", "build", "-t", "misosoup_test_container", "."], check=False
    )
    complete_process = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--name",
            "misosoup_test_container_run",
            "misosoup_test_container",
            "misosoup",
            "-h",
        ],
        check=False,
    )
    assert complete_process.returncode == 0


def test_integration():
    """Run docker container on data."""
    complete_process = subprocess.run(
        [
            "misosoup",
            "--base-medium",
            "tests/data/medium.yaml",
            "--carbon-sources",
            "ac",
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
    out = yaml.safe_load("\n".join(str(complete_process.stdout).split("\\n")[2:-1]))
    assert out["ac"]["A1R12"][0]["y_A1R12"] == 1
    assert out["ac"]["A1R12"][0]["y_I2R16"] == 1