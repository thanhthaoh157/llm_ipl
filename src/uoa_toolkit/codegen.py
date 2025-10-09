"""Helpers for emitting ready-to-run Python snippets."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import textwrap

__all__ = [
    "generate_auto_democratic_peace_snippet",
    "generate_run_snippet",
]


def _format_path(path: Optional[Path]) -> str:
    if path is None:
        return "None"
    return f"Path({path.as_posix()!r})"


def generate_run_snippet(recipe_path: Path, output_dir: Optional[Path] = None) -> str:
    """Return a Python snippet that executes the provided recipe."""

    recipe_arg = _format_path(recipe_path.resolve())
    output_arg = _format_path(output_dir.resolve() if output_dir else None)

    snippet = f"""
from pathlib import Path
from uoa_toolkit.workflows import execute_recipe

result = execute_recipe(
    {recipe_arg},
    output_dir={output_arg},
)

print(f"Exports written to {{result.recipe.output.directory}}")
for name, path in result.exports.items():
    print(f"  {{name}} -> {{path}}")
"""
    return textwrap.dedent(snippet).strip()


def generate_auto_democratic_peace_snippet(
    *,
    model: str,
    data_root: Path,
    output_dir: Optional[Path] = None,
    response_path: Optional[Path] = None,
) -> str:
    """Return a Python snippet that reproduces the democratic peace workflow."""

    data_root_arg = _format_path(data_root.resolve())
    output_arg = _format_path(output_dir.resolve() if output_dir else None)
    response_arg = _format_path(response_path.resolve() if response_path else None)

    snippet = f"""
from pathlib import Path
from uoa_toolkit.workflows import run_democratic_peace_workflow

result = run_democratic_peace_workflow(
    output_dir={output_arg},
    model={model!r},
    data_root={data_root_arg},
    response_path={response_arg},
)

print(f"Prompt\\n------\\n{{result.prompt}}")
print(f"Recipe saved to {{result.recipe_path}}")
for name, path in result.exports.items():
    print(f"  {{name}} -> {{path}}")
"""
    return textwrap.dedent(snippet).strip()
