"""Web front-ends for the UOA toolkit using FastAPI and Flask."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .config import load_recipe
from .export import export_outputs
from .joiner import build_panel
from .manifest import build_manifest

try:  # pragma: no cover - FastAPI is optional at runtime
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover - exercised in tests via dependency guards
    FastAPI = None  # type: ignore
    HTTPException = None  # type: ignore
    HTMLResponse = None  # type: ignore
    BaseModel = object  # type: ignore

try:  # pragma: no cover - Flask is optional at runtime
    from flask import Flask, jsonify, request
except ModuleNotFoundError:  # pragma: no cover - exercised in tests via dependency guards
    Flask = None  # type: ignore
    jsonify = None  # type: ignore
    request = None  # type: ignore


class RunResponse(dict):
    """Typed alias for web responses."""


def _run_recipe(
    recipe_path: Path,
    *,
    output_dir: Optional[Path] = None,
    formats: Optional[List[str]] = None,
) -> RunResponse:
    """Execute a recipe and structure the response payload."""

    recipe_path = recipe_path.expanduser().resolve()
    recipe = load_recipe(recipe_path)

    if output_dir is not None:
        recipe.output.directory = output_dir.expanduser().resolve()
    if formats:
        recipe.output.formats = list(formats)

    panel = build_panel(recipe)
    manifest = build_manifest(recipe, panel)
    exported = export_outputs(
        panel,
        manifest["dictionary"],
        manifest["entries"],
        manifest["metadata"],
        recipe.output.directory,
        recipe.output.file_name,
        recipe.output.formats,
    )

    return RunResponse(
        recipe=recipe.name,
        description=recipe.description or "",
        row_count=panel.height,
        column_count=panel.width,
        exports={name: str(path) for name, path in exported.items()},
        dictionary=manifest["dictionary"].rows,
        metadata=manifest["metadata"].rows,
        manifest=[asdict(entry) for entry in manifest["entries"]],
    )


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>UOA Toolkit Web</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }
    code { background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 0.25rem; }
    header { margin-bottom: 1.5rem; }
  </style>
</head>
<body>
  <header>
    <h1>UOA Toolkit Web Console</h1>
    <p>Trigger recipe executions via FastAPI or Flask.</p>
  </header>
  <section>
    <h2>Quick start</h2>
    <ol>
      <li>POST JSON to <code>/api/run</code> with a <code>recipe_path</code> and optional <code>output_dir</code>.</li>
      <li>Receive export locations plus manifest metadata in the response.</li>
    </ol>
    <p>The sample recipe lives at <code>recipes/sample.yaml</code>.</p>
  </section>
</body>
</html>"""


def create_fastapi_app() -> "FastAPI":
    """Create a FastAPI application exposing the run endpoint."""

    if FastAPI is None or HTTPException is None or HTMLResponse is None:
        raise RuntimeError("FastAPI is not available. Install the 'fastapi' extra to enable the web app.")

    class RunRequestModel(BaseModel):
        recipe_path: str
        output_dir: Optional[str] = None
        formats: Optional[List[str]] = None

    app = FastAPI(title="UOA Toolkit", description="Execute recipes via HTTP")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _HTML_TEMPLATE

    @app.post("/api/run")
    def run(request: RunRequestModel) -> RunResponse:
        try:
            output_dir = Path(request.output_dir) if request.output_dir else None
            return _run_recipe(Path(request.recipe_path), output_dir=output_dir, formats=request.formats)
        except FileNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except Exception as error:  # pragma: no cover - unexpected runtime errors
            raise HTTPException(status_code=500, detail=str(error)) from error

    return app


def create_flask_app() -> "Flask":
    """Create a Flask application exposing the same endpoints."""

    if Flask is None or jsonify is None or request is None:
        raise RuntimeError("Flask is not available. Install the 'flask' extra to enable the web app.")

    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return _HTML_TEMPLATE

    @app.post("/api/run")
    def run() -> object:
        payload = request.get_json(force=True, silent=True) or {}
        recipe_path = payload.get("recipe_path")
        output_dir_raw = payload.get("output_dir")
        formats_raw = payload.get("formats")

        if not recipe_path:
            return jsonify({"error": "recipe_path is required"}), 400

        try:
            output_dir = Path(output_dir_raw) if output_dir_raw else None
            formats = list(formats_raw) if formats_raw else None
            response = _run_recipe(Path(recipe_path), output_dir=output_dir, formats=formats)
            return jsonify(response)
        except FileNotFoundError as error:
            return jsonify({"error": str(error)}), 404
        except Exception as error:  # pragma: no cover - unexpected runtime errors
            return jsonify({"error": str(error)}), 500

    return app


__all__ = ["create_fastapi_app", "create_flask_app"]
