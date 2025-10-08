"""Typer CLI entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

try:  # pragma: no cover - runtime import guard
    import typer
except ModuleNotFoundError:  # pragma: no cover - exercised in tests
    from .typer_stub import typer

from .config import load_recipe
from .export import export_outputs
from .joiner import build_panel
from .llm import OpenRouterError, call_openrouter, democratic_peace_prompt
from .manifest import build_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "recipes"

app = typer.Typer(add_completion=False, help="Build analytical panels from declarative recipes.")


def _build_panel(recipe):
    panel = build_panel(recipe)
    manifest = build_manifest(recipe, panel)
    return panel, manifest


def _prepare_recipe_file(
    recipe_text: str,
    destination: Path,
    *,
    data_root: Path,
    output_dir: Optional[Path],
) -> Path:
    """Persist a generated recipe to disk and normalise connector paths."""

    destination.mkdir(parents=True, exist_ok=True)
    raw = yaml.safe_load(recipe_text)
    if not isinstance(raw, dict):
        raise ValueError("OpenRouter response did not contain a YAML mapping")

    sections = [raw.get("uoa", {})] + list(raw.get("datasets", []))
    for section in sections:
        if not isinstance(section, dict):
            continue
        connector = section.get("connector", {})
        path_value = connector.get("path")
        if not path_value:
            continue
        candidate = Path(path_value).expanduser()
        if not candidate.is_absolute():
            normalized = (data_root / candidate).resolve()
            if normalized.exists():
                connector["path"] = str(normalized)

    output_cfg = raw.setdefault("output", {})
    if output_dir is not None:
        output_cfg["directory"] = str(output_dir.resolve())
    else:
        output_cfg.setdefault("directory", str(destination.resolve()))
    output_cfg.setdefault("file_name", "democratic_peace_panel.xlsx")
    output_cfg.setdefault("formats", ["excel", "csv"])

    recipe_path = destination / "democratic_peace.yaml"
    with recipe_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(raw, handle, sort_keys=False)
    return recipe_path



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


@app.command("auto-democratic-peace")
def auto_democratic_peace(
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        help="Directory where the generated panel and artifacts will be written.",
    ),
    model: str = typer.Option(
        "openrouter/anthropic/claude-3.5-sonnet",
        "--model",
        help="OpenRouter model identifier to query.",
    ),
    data_root: Path = typer.Option(
        DEFAULT_DATA_ROOT,
        "--data-root",
        help="Root directory that holds the CSV assets referenced by the recipe.",
    ),
    response_path: Optional[Path] = typer.Option(
        None,
        "--response-path",
        help="Bypass the API and load a stored OpenRouter response (useful for tests).",
    ),
) -> None:
    """Generate and execute a democratic peace recipe via the OpenRouter API."""

    prompt = democratic_peace_prompt()
    typer.echo("Prepared OpenRouter prompt for democratic peace recipe:")
    typer.echo(prompt)

    if response_path is not None:
        recipe_text = response_path.read_text(encoding="utf-8")
    else:
        try:
            response = call_openrouter(prompt, model=model)
        except OpenRouterError as error:
            typer.echo(f"Failed to call OpenRouter: {error}", err=True)
            raise typer.Exit(code=1)
        recipe_text = response.content

    target_dir = (output_dir or (Path.cwd() / "democratic_peace_run")).resolve()
    recipe_path = _prepare_recipe_file(
        recipe_text,
        target_dir,
        data_root=data_root.resolve(),
        output_dir=output_dir.resolve() if output_dir else None,
    )

    recipe = load_recipe(recipe_path)
    if output_dir is not None:
        recipe.output.directory = output_dir.resolve()

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

    typer.echo(f"Generated democratic peace panel via OpenRouter into {recipe.output.directory}")


if __name__ == "__main__":  # pragma: no cover
    app()
