# International Relations Quantitative Analysis Toolkit

The **UOA Toolkit** packages everything needed to prototype country-level or dyadic
panels for international relations research. Recipes describe the unit of analysis,
inputs, join logic, and the desired export artefacts so complex data engineering
flows can be reproduced with a single command.

## Why this toolkit?

- **Quant IR focus.** Bundled sample data and workflows mirror democratic peace
  and regime-type studies, plus scaffolding for MGIMO-hosted sources such as
  Polity, COW, Archigos, ATOP, and others listed in [`data/README.md`](data/README.md).
- **Declarative recipes.** Structured YAML is parsed into Pydantic-style models
  (`src/uoa_toolkit/config.py`) so joins, renames, filters, and exports are
  validated before execution.
- **Embedded execution engine.** Lightweight table utilities (based on Polars-like
  operations) live in-repo, covering CSV ingestion, left and as-of joins, and
  manifest/dictionary creation with no external database dependency.
- **Automation everywhere.** The CLI can execute recipes, drive an
  OpenRouter-powered democratic peace workflow, emit runnable Python scripts,
  validate/download MGIMO datasets, or expose the same behaviour over FastAPI and
  Flask.

## Installation

```bash
pip install -e .
```

Python ≥3.9 is required. The project metadata declares recommended extras such
as Polars, DuckDB, Pydantic, Typer, FastAPI, Flask, and Uvicorn; lightweight
fallbacks are vendored so the toolkit works in restricted environments too.

## End-to-end workflow (country-year example)

1. **Inspect the recipe.** `recipes/sample.yaml` specifies a country–year panel
   combining population, trade, and attribute tables with a manifest definition.
2. **Run the CLI.**
   ```bash
   python -m uoa_toolkit.cli run recipes/sample.yaml --output-dir outputs/sample
   ```
3. **Review outputs.** The command generates:
   - `panel.parquet`, `panel.csv`, and an Excel workbook with data, dictionary,
     and manifest sheets.
   - `manifest.json` describing provenance, joins, and exports.

Need to embed this inside notebooks or automation pipelines? Ask the CLI to emit
runnable Python code instead of executing the recipe:

```bash
python -m uoa_toolkit.cli run recipes/sample.yaml \
    --output-dir outputs/sample \
    --emit-code --dry-run
```

The emitted snippet uses `uoa_toolkit.workflows.execute_recipe` so the same
workflow can be orchestrated from custom scripts or schedulers.

## Democratic peace automation (OpenRouter)

1. Export an OpenRouter API key as `OPENROUTER_API_KEY`.
2. Launch the automated run:
   ```bash
   python -m uoa_toolkit.cli auto-democratic-peace --output-dir outputs/peace
   ```
3. For offline validation, reuse the cached response bundled at
   `recipes/democratic_peace/openrouter_response.yaml`:
   ```bash
   python -m uoa_toolkit.cli auto-democratic-peace \
       --response-path recipes/democratic_peace/openrouter_response.yaml \
       --output-dir outputs/peace
   ```
4. To obtain the equivalent Python script without running it, add
   `--emit-code --dry-run`.

The workflow reproduces an IR classic: joining conflict events, dyads, and regime
data into an analysis-ready panel while logging the model conversation in the
manifest.

## MGIMO dataset automation

MGIMO-affiliated datasets cannot be redistributed, but the toolkit provides a
catalogue and downloader to stage them under `data/mgimo/`:

```bash
python -m uoa_toolkit.cli download-datasets --all --output-root data/mgimo
```

Each dataset is resolved against authoritative URLs (Polity, COW, ATOP, ICOW,
PRIO, etc.). When a source requires registration or license acceptance, the CLI
emits instructions instead of attempting an unauthorised download. Pair this with
`python -m uoa_toolkit.cli validate-mgimo` to ensure directories and checksum
metadata are in sync.

## Programmatic usage in Python

```python
from pathlib import Path

from uoa_toolkit.workflows import execute_recipe

recipe = Path("recipes/sample.yaml")
outputs = Path("outputs/sample_python")
workflow_result = execute_recipe(recipe_path=recipe, output_dir=outputs)

print(workflow_result.manifest.path)
for export in workflow_result.exports:
    print(export.format, export.path)
```

`execute_recipe` returns a dataclass with manifest metadata and export
information, enabling downstream quantitative analysis pipelines to chain joins
with statistical modelling libraries (Statsmodels, PyMC, scikit-learn, etc.).

## Web interfaces

FastAPI and Flask applications expose the same `/api/run` endpoint used by the
CLI:

```bash
uvicorn uoa_toolkit.web:create_fastapi_app --factory --reload
# or
flask --app uoa_toolkit.web:create_flask_app --debug run
```

Submit a job with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"recipe_path": "recipes/sample.yaml", "output_dir": "outputs/web"}'
```

Responses contain manifest metadata and the export paths so you can chain web
requests to notebook-based analysis or dashboards.

## Testing

Run the full automated test suite (CLI, downloader, web endpoints):

```bash
pytest
```

The suite includes smoke tests that execute the sample recipe, democratic peace
workflow, dataset validation, and optional FastAPI/Flask endpoint checks.

---

Questions, improvements, or new datasets for IR analysis? Open an issue or adapt
the recipes—everything needed to reproduce the pipelines is in this repository.
