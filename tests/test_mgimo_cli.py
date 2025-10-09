"""CLI tests for MGIMO dataset validation helpers."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_validate_mgimo_creates_structure(tmp_path):
    data_root = tmp_path / "mgimo"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uoa_toolkit.cli",
            "validate-mgimo",
            str(data_root),
            "--create-dirs",
            "--allow-empty",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "Missing dataset directories" not in result.stdout
    assert "Warning" in result.stdout

    expected_dirs = {
        "polity_iv",
        "cow_major_power_indicator",
        "archigos",
        "lead",
        "cow_national_capabilities",
        "ipe_data_resource",
        "historic_bond_yields",
        "migration",
        "cow_contiguity",
        "capital_distance",
        "cshapes_distance",
        "cow_interstate_war",
        "cow_intrastate_war",
        "prio_intrastate_war",
        "mid",
        "icb",
        "compellent_threats",
        "icow",
        "terrorism_incidents",
        "atop_alliances",
        "cow_alliances",
        "igo_memberships",
        "joint_igo_memberships",
        "s_similarity",
        "tau_b_similarity",
        "nuclear_deployments",
        "nuclear_cooperation",
    }

    actual = {path.name for path in data_root.iterdir() if path.is_dir()}
    assert expected_dirs == actual
