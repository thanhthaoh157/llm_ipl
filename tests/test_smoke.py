"""Smoke test for the CLI."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_cli_generates_excel(tmp_path):
    recipe_path = Path("recipes/sample.yaml").resolve()
    output_dir = tmp_path / "outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uoa_toolkit.cli",
            "run",
            str(recipe_path),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "Exported panel" in result.stdout
    expected_file = output_dir / "sample_panel.xlsx"
    assert expected_file.exists()


def test_cli_emit_code_snippet(tmp_path):
    recipe_path = Path("recipes/sample.yaml").resolve()
    output_dir = tmp_path / "dry_run_outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uoa_toolkit.cli",
            "run",
            str(recipe_path),
            "--output-dir",
            str(output_dir),
            "--emit-code",
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "execute_recipe" in result.stdout
    assert "Exports written to" in result.stdout
    assert not output_dir.exists()
