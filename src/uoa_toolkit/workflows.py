"""High-level workflows that orchestrate recipe execution and exports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from .config import RecipeConfig, load_recipe
from .export import export_outputs
from .joiner import build_panel
from .llm import OpenRouterError, call_openrouter, democratic_peace_prompt
from .manifest import build_manifest

__all__ = [
    "WorkflowResult",
    "build_panel_and_manifest",
    "execute_recipe",
    "prepare_recipe_file",
    "run_democratic_peace_workflow",
]


@dataclass
class WorkflowResult:
    """Container describing the outcome of a workflow run."""

    recipe: RecipeConfig
    panel_path: Path
    exports: dict[str, Path]
    manifest: dict[str, object]
    prompt: Optional[str] = None
    recipe_path: Optional[Path] = None


def build_panel_and_manifest(recipe: RecipeConfig):
    """Return the assembled panel and manifest tables for a recipe."""

    panel = build_panel(recipe)
    manifest = build_manifest(recipe, panel)
    return panel, manifest


def execute_recipe(recipe_path: Path, output_dir: Optional[Path] = None) -> WorkflowResult:
    """Execute a recipe, export its artefacts, and return metadata."""

    recipe = load_recipe(recipe_path)
    if output_dir is not None:
        recipe.output.directory = output_dir

    panel, manifest = build_panel_and_manifest(recipe)
    exports = export_outputs(
        panel,
        manifest["dictionary"],
        manifest["entries"],
        manifest["metadata"],
        recipe.output.directory,
        recipe.output.file_name,
        recipe.output.formats,
    )

    panel_path = exports.get("excel") or next(iter(exports.values()))
    return WorkflowResult(
        recipe=recipe,
        panel_path=panel_path,
        exports=exports,
        manifest=manifest,
        recipe_path=recipe_path,
    )


def prepare_recipe_file(
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
        if not isinstance(connector, dict):
            continue
        path_value = connector.get("path")
        if not path_value:
            continue
        candidate = Path(path_value).expanduser()
        if not candidate.is_absolute():
            normalized = (data_root / candidate).resolve()
            if normalized.exists():
                connector["path"] = str(normalized)

    output_cfg = raw.setdefault("output", {})
    if not isinstance(output_cfg, dict):
        raise ValueError("Recipe output configuration must be a mapping")

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


def run_democratic_peace_workflow(
    *,
    output_dir: Optional[Path],
    model: str,
    data_root: Path,
    response_path: Optional[Path] = None,
    response_text: Optional[str] = None,
    prompt: Optional[str] = None,
) -> WorkflowResult:
    """Automate the democratic peace workflow via OpenRouter or cached responses."""

    prompt = democratic_peace_prompt() if prompt is None else prompt

    if response_text is None:
        if response_path is not None:
            response_text = response_path.read_text(encoding="utf-8")
        else:
            try:
                response = call_openrouter(prompt, model=model)
            except OpenRouterError as error:
                raise RuntimeError(f"Failed to call OpenRouter: {error}") from error
            response_text = response.content

    target_dir = (output_dir or (Path.cwd() / "democratic_peace_run")).resolve()
    recipe_path = prepare_recipe_file(
        response_text,
        target_dir,
        data_root=data_root.resolve(),
        output_dir=output_dir.resolve() if output_dir else None,
    )

    result = execute_recipe(recipe_path, output_dir=output_dir)
    result.prompt = prompt
    result.recipe_path = recipe_path
    return result
