# UOA Toolkit

This repository contains a minimal, recipe-driven toolkit for building unit-of-analysis (UOA) panels. Recipes describe input datasets, how to join them, and the export artefacts to produce.

## Features

- Declarative YAML recipes parsed into strongly-typed dataclasses.
- Lightweight in-repo table engine that provides CSV ingestion, joins (including as-of joins), and export helpers without external dependencies.
- Automated manifest and data dictionary generation.
- Typer-style CLI (with an in-repo fallback implementation) that exports Excel, CSV, and Parquet outputs.
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

### Working with MGIMO-sourced datasets

The real-world datasets requested by the user (Polity IV, COW series, Archigos, etc.)
are hosted on the MGIMO data portal and cannot be redistributed in this repository.
Instead, reserve the `data/mgimo/` directory for the official downloads and validate
your local copy with the helper command:

```bash
python -m uoa_toolkit.cli validate-mgimo data/mgimo --create-dirs
```

Re-run the command after copying the downloaded CSV/TSV/Parquet/Excel files into the
matching subdirectories. The command prints any missing or empty dataset folders and
references `data/README.md` for the full catalogue.

## Testing

Run the test suite to verify the CLI flows end-to-end:

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
