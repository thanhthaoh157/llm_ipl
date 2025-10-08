"""Typer CLI entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:  # pragma: no cover - runtime import guard
    import typer
except ModuleNotFoundError:  # pragma: no cover - exercised in tests
    from .typer_stub import typer

from .config import load_recipe
from .export import export_outputs
from .joiner import build_panel
from .manifest import build_manifest

app = typer.Typer(add_completion=False, help="Build analytical panels from declarative recipes.")


def _build_panel(recipe):
    panel = build_panel(recipe)
    manifest = build_manifest(recipe, panel)
    return panel, manifest


@app.command()
def run(
    recipe_path: Path = typer.Argument(..., help="Path to the YAML recipe file."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory."),
) -> None:
    """Execute a recipe and export the resulting panel."""

    recipe = load_recipe(recipe_path)
    if output_dir is not None:
        recipe.output.directory = output_dir

    panel, manifest = _build_panel(recipe)

    export_outputs(
        panel,
        manifest["dictionary"],
        manifest["entries"],
        manifest["metadata"],
        recipe.output.directory,
        recipe.output.file_name,
        recipe.output.formats,
    )

    typer.echo(f"Exported panel to {recipe.output.directory}")


if __name__ == "__main__":  # pragma: no cover
    app()
