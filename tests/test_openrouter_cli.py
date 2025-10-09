"""Tests for the OpenRouter-assisted democratic peace workflow."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_auto_democratic_peace_cli(tmp_path):
    response_path = Path("recipes/democratic_peace/openrouter_response.yaml").resolve()
    output_dir = tmp_path / "democratic_peace_outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uoa_toolkit.cli",
            "auto-democratic-peace",
            "--response-path",
            str(response_path),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "Generated democratic peace panel" in result.stdout
    expected_panel = output_dir / "democratic_peace_panel.xlsx"
    assert expected_panel.exists()


def test_auto_democratic_peace_emit_code(tmp_path):
    response_path = Path("recipes/democratic_peace/openrouter_response.yaml").resolve()
    output_dir = tmp_path / "democratic_peace_outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uoa_toolkit.cli",
            "auto-democratic-peace",
            "--response-path",
            str(response_path),
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

    assert "run_democratic_peace_workflow" in result.stdout
    assert "Prompt" in result.stdout
    assert not output_dir.exists()
