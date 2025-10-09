"""Typer CLI entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:  # pragma: no cover - runtime import guard
    import typer
except ModuleNotFoundError:  # pragma: no cover - exercised in tests
    from .typer_stub import typer

from .codegen import (
    generate_auto_democratic_peace_snippet,
    generate_run_snippet,
)
from .datasets import summarise_reports, validate_mgimo_datasets
from .downloader import (
    DownloadError,
    generate_python_snippet,
    list_datasets,
    download_datasets as download_multiple,
)
from .llm import democratic_peace_prompt
from .workflows import execute_recipe, run_democratic_peace_workflow

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "recipes"
DEFAULT_DATA_DOWNLOAD_ROOT = PROJECT_ROOT / "data" / "mgimo"

app = typer.Typer(add_completion=False, help="Build analytical panels from declarative recipes.")



@app.command()
def run(
    recipe_path: Path = typer.Argument(..., help="Path to the YAML recipe file."),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory."),
    emit_code: bool = typer.Option(
        False,
        "--emit-code",
        help="Print a Python snippet that replicates the run workflow.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Skip execution (useful together with --emit-code).",
    ),
) -> None:
    """Execute a recipe and export the resulting panel."""

    if emit_code:
        typer.echo(generate_run_snippet(recipe_path, output_dir))
        if dry_run:
            return

    if dry_run:
        return

    result = execute_recipe(recipe_path, output_dir=output_dir)
    typer.echo(f"Exported panel to {result.recipe.output.directory}")


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
    emit_code: bool = typer.Option(
        False,
        "--emit-code",
        help="Print a Python snippet that replicates the automated workflow.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Skip execution (useful when only the snippet is required).",
    ),
) -> None:
    """Generate and execute a democratic peace recipe via the OpenRouter API."""

    prompt = democratic_peace_prompt()
    typer.echo("Prepared OpenRouter prompt for democratic peace recipe:")
    typer.echo(prompt)

    if emit_code:
        typer.echo(
            generate_auto_democratic_peace_snippet(
                model=model,
                data_root=data_root,
                output_dir=output_dir,
                response_path=response_path,
            )
        )
        if dry_run:
            return

    if dry_run:
        return

    try:
        result = run_democratic_peace_workflow(
            output_dir=output_dir,
            model=model,
            data_root=data_root,
            response_path=response_path,
            prompt=prompt,
        )
    except RuntimeError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1)

    typer.echo(
        f"Generated democratic peace panel via OpenRouter into {result.recipe.output.directory}"
    )


@app.command("validate-mgimo")
def validate_mgimo(
    data_root: Path = typer.Argument(
        Path("data/mgimo"),
        help="Root directory that should contain MGIMO dataset downloads.",
    ),
    create_dirs: bool = typer.Option(
        False,
        "--create-dirs",
        help="Create the expected directory structure if it is missing.",
    ),
    allow_empty: bool = typer.Option(
        False,
        "--allow-empty",
        help="Do not treat empty dataset directories as an error (useful during setup).",
    ),
) -> None:
    """Validate that MGIMO datasets have been downloaded into the workspace."""

    reports = validate_mgimo_datasets(data_root, create_dirs=create_dirs)
    missing_dirs, empty_dirs = summarise_reports(reports)

    if missing_dirs:
        typer.echo("Missing dataset directories:")
        for report in missing_dirs:
            typer.echo(f"  - {report.spec.title} [{report.spec.slug}] -> {report.directory}")

    if empty_dirs:
        prefix = "Warning" if allow_empty else "Datasets without recognised files"
        typer.echo(f"{prefix}:")
        for report in empty_dirs:
            typer.echo(f"  - {report.spec.title} [{report.spec.slug}] -> {report.directory}")


@app.command("download-datasets")
def download_datasets(
    slugs: list[str] = typer.Argument(
        None,
        help="One or more dataset slugs to download (defaults to all supported datasets).",
    ),
    data_root: Path = typer.Option(
        DEFAULT_DATA_DOWNLOAD_ROOT,
        "--data-root",
        help="Directory where downloaded datasets should be stored.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Re-download files even if they already exist.",
    ),
    emit_code: bool = typer.Option(
        False,
        "--emit-code",
        help="Print a ready-to-run Python snippet that performs the same downloads.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Do not download files; only report which datasets would be fetched.",
    ),
) -> None:
    """Download the official datasets referenced by the MGIMO workflow."""

    known = {dataset.slug: dataset for dataset in list_datasets()}
    if not slugs:
        selected_slugs = list(known)
    else:
        missing = [slug for slug in slugs if slug not in known]
        if missing:
            raise typer.BadParameter(
                f"Unknown dataset slug(s): {', '.join(sorted(missing))}",
                param_hint="slugs",
            )
        selected_slugs = slugs

    if emit_code:
        snippet = generate_python_snippet(selected_slugs, data_root)
        typer.echo(snippet)
        if dry_run:
            return

    for slug in selected_slugs:
        dataset = known[slug]
        typer.echo(f"Preparing {dataset.title} [{dataset.slug}] from {dataset.landing_page}")
        if dataset.requires_manual_steps or not dataset.supports_automation():
            typer.echo(
                "  - manual action required; visit the landing page to download the data",
                err=True,
            )
            continue
        if dry_run:
            continue
        try:
            destination_map = download_multiple([slug], data_root, overwrite=overwrite)
        except DownloadError as error:
            typer.echo(f"  - failed: {error}", err=True)
            continue
        destination = destination_map[slug]
        typer.echo(f"  - saved to {destination}")


if __name__ == "__main__":  # pragma: no cover
    app()
