# International Relations Quantitative Analysis Playbook

This playbook shows how to reproduce a small-scale democratic peace workflow with
this repository. It combines shell commands, Python snippets, and narrative
explanations so the entire process can be executed step by step.

## 1. Set up the environment

Install the project in editable mode and ensure optional dependencies (Polars,
DuckDB, Typer, FastAPI, Flask) are available. The toolkit provides fallbacks if
some libraries are missing.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2. Inspect the recipe

The democratic peace sample recipe defines a dyadic unit of analysis, input
connectors, join configuration, and exports. Open the file to understand the
structure and metadata requirements.

```bash
bat recipes/democratic_peace/recipe.yaml || cat recipes/democratic_peace/recipe.yaml
```

Key sections include:

- `unit_of_analysis`: dyad-year grain with COW-style identifiers.
- `sources`: CSV connectors for dyads, conflicts, regime attributes, and
  population baselines.
- `transforms`: left joins and as-of merges implemented via the in-repo table
  engine.
- `exports`: Parquet, CSV, and Excel outputs plus a manifest summarising lineage.

## 3. Execute via CLI

Run the CLI to materialise the dataset. The command creates a manifest, data
outputs, and a data dictionary sheet inside the Excel workbook.

```bash
python -m uoa_toolkit.cli run recipes/democratic_peace/recipe.yaml \
    --output-dir outputs/democratic_peace
```

The manifest includes join order, column provenance, and OpenRouter LLM
interactions (if a live call is made).

## 4. Automate with OpenRouter

For a full end-to-end automation that generates the recipe, fetches data, and
runs the joins, use the dedicated workflow. Provide an API key through the
`OPENROUTER_API_KEY` environment variable.

```bash
export OPENROUTER_API_KEY="sk-or-example"
python -m uoa_toolkit.cli auto-democratic-peace \
    --output-dir outputs/auto_democratic_peace
```

Offline validation is possible by replaying the cached conversation shipped with
the repository:

```bash
python -m uoa_toolkit.cli auto-democratic-peace \
    --response-path recipes/democratic_peace/openrouter_response.yaml \
    --output-dir outputs/auto_democratic_peace_cached
```

## 5. Embed into Python workflows

The toolkit exposes `execute_recipe` so the same recipe can be orchestrated from
Python scripts, notebooks, or batch jobs.

```python
from pathlib import Path
from uoa_toolkit.workflows import execute_recipe

recipe_path = Path("recipes/democratic_peace/recipe.yaml")
output_dir = Path("outputs/democratic_peace_python")

result = execute_recipe(recipe_path=recipe_path, output_dir=output_dir)
print(result.manifest.path)
for export in result.exports:
    print(export.format, export.path)
```

## 6. Validate MGIMO dataset staging

The repository cannot redistribute MGIMO-affiliated sources, but it provides a
catalogue and downloader stub. Use these commands to stage the directories and
confirm which downloads are pending.

```bash
python -m uoa_toolkit.cli download-datasets --all --output-root data/mgimo
python -m uoa_toolkit.cli validate-mgimo --root data/mgimo
```

Each entry prints actionable guidance, including whether manual registration or
license acceptance is required.

## 7. Reproduce via web APIs

The same recipe execution can be invoked through FastAPI or Flask. Launch a
server in one terminal and submit jobs with HTTP requests from another.

```bash
uvicorn uoa_toolkit.web:create_fastapi_app --factory --reload
```

Then issue a request:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"recipe_path": "recipes/democratic_peace/recipe.yaml", "output_dir": "outputs/web"}'
```

The JSON response lists the manifest and export paths, making it straightforward
to integrate with dashboards or workflow orchestrators.

## 8. Run automated tests

Validate that the entire stack—including CLI workflows, OpenRouter automation,
MGIMO helpers, and web endpoints—works as expected.

```bash
pytest
```

The test suite executes smoke runs of the sample recipe and democratic peace
workflows, providing quick feedback on pipeline integrity.

---

With these steps you can reproduce a complete international relations data
assembly process, from declarative recipe inspection to programmatic analysis
and web-based orchestration.
