# UOA Toolkit

This repository contains a minimal, recipe-driven toolkit for building unit-of-analysis (UOA) panels. Recipes describe input datasets, how to join them, and the export artefacts to produce.

## Features

- Declarative YAML recipes parsed into strongly-typed dataclasses.
- Lightweight in-repo table engine that provides CSV ingestion, joins (including as-of joins), and export helpers without external dependencies.
- Automated manifest and data dictionary generation.
- Typer-style CLI (with an in-repo fallback implementation) that exports Excel, CSV, and Parquet outputs.
- FastAPI and Flask applications that expose the same recipe execution workflow over HTTP.
- OpenRouter integration that can draft and execute a democratic peace recipe end-to-end.
- Smoke tests that exercise both the static sample recipe and the OpenRouter-assisted workflow.

## Getting started

### Prerequisites

- Python 3.9 or later
- `pip` for managing dependencies

### Installation

```bash
pip install -e .
```

The repository vendors lightweight stand-ins for heavier dependencies so the project can run in constrained environments, but the published metadata still lists recommended packages such as Polars, DuckDB, Pydantic, and Typer.

### Running the sample recipe

```bash
python -m uoa_toolkit.cli run recipes/sample.yaml --output-dir outputs
```

The command reads the `recipes/sample.yaml` file, joins the configured datasets, and writes Excel/CSV/Parquet outputs (including a data dictionary and manifest sheets) into the `outputs/` directory.

### Automating a democratic peace panel with OpenRouter

1. Obtain an OpenRouter API key and expose it as `OPENROUTER_API_KEY` in your environment.
2. Run the automated workflow:

   ```bash
   python -m uoa_toolkit.cli auto-democratic-peace --output-dir peace_outputs
   ```

   The CLI submits a structured prompt (`uoa_toolkit.llm.democratic_peace_prompt`) to OpenRouter, stores the returned YAML recipe, normalises connector paths to the `recipes/democratic_peace/` sample data, and exports Excel/CSV outputs ready for inspection.

3. For offline or testing scenarios, reuse the bundled response without hitting the API:

   ```bash
   python -m uoa_toolkit.cli auto-democratic-peace \
       --response-path recipes/democratic_peace/openrouter_response.yaml \
       --output-dir peace_outputs
   ```

### Developing new recipes

1. Copy the sample recipe file and update dataset paths, join keys, and export preferences.
2. CSV connector paths can be absolute or relative to the recipe file.
3. Optionally configure `select`, `rename`, or `prefix` to control the exported column names.

### Serving the toolkit on the web

The project provides both FastAPI and Flask front-ends. They expose identical endpoints: a
landing page at `/` and an `/api/run` POST endpoint that accepts JSON with a `recipe_path`,
optional `output_dir`, and optional `formats` array. Responses include the manifest metadata
and the exported file locations.

Run the FastAPI variant with Uvicorn:

```bash
uvicorn uoa_toolkit.web:create_fastapi_app --factory --reload
```

Or launch the Flask server:

```bash
flask --app uoa_toolkit.web:create_flask_app --debug run
```

Submit the sample recipe for processing with `curl` or similar tools:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"recipe_path": "recipes/sample.yaml", "output_dir": "web_outputs"}'
```

The HTTP response lists the generated files and provides the dictionary and manifest records.

### Working with MGIMO-sourced datasets

The real-world datasets requested by the user (Polity IV, COW series, Archigos, etc.)
are hosted on external portals and cannot be redistributed here. The toolkit now ships
an automated downloader that targets the official sources listed in `data/README.md`.

To fetch every dataset with a published direct download URL into `data/mgimo/`, run:

```bash
python -m uoa_toolkit.cli download-datasets
```

The command prints progress for each dataset. When a source requires manual steps (for
example, the Global Terrorism Database’s licence agreement), the CLI flags the dataset
and points to the landing page.

Need to embed the workflow in another script? Ask the CLI to emit the equivalent Python
code:

```bash
python -m uoa_toolkit.cli download-datasets --emit-code --dry-run
```

Once the downloads are present, validate and scaffold the directory layout:

```bash
python -m uoa_toolkit.cli validate-mgimo data/mgimo --create-dirs
```

Re-run the validation after extracting archives or adding new files. The command prints
any missing or empty dataset folders and references `data/README.md` for the full
catalogue.

## Testing

Run the test suite to verify the CLI and web flows end-to-end:

```bash
pytest
```

The tests build both the sample panel and the democratic peace panel in temporary directories and confirm that the Excel outputs are generated.

## Project structure

- `pyproject.toml`: Project metadata and dependencies.
- `src/uoa_toolkit/`: Source code for configuration, connectors, joins, exports, LLM helpers, and CLI entry point.
- `recipes/`: Example recipes, OpenRouter responses, and input data for quick verification.
- `tests/`: Automated tests.

## License

This project is provided as-is for demonstration purposes.
