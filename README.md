# UOA Toolkit

This repository contains a minimal, recipe-driven toolkit for building unit-of-analysis (UOA) panels. Recipes describe input datasets, how to join them, and the export artefacts to produce.

## Features

- Declarative YAML recipes parsed into strongly-typed dataclasses.
- Lightweight in-repo table engine that provides CSV ingestion, joins (including as-of joins), and export helpers without external dependencies.
- Automated manifest and data dictionary generation.
- Typer-style CLI (with an in-repo fallback implementation) that exports Excel, CSV, and Parquet outputs.
- Smoke test that exercises the CLI end-to-end with sample data.

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

### Developing new recipes

1. Copy the sample recipe file and update dataset paths, join keys, and export preferences.
2. CSV connector paths can be absolute or relative to the recipe file.
3. Optionally configure `select`, `rename`, or `prefix` to control the exported column names.

## Testing

Run the smoke test to verify the CLI end-to-end:

```bash
pytest
```

The smoke test builds the sample panel in a temporary directory and confirms that the Excel output is generated.

## Project structure

- `pyproject.toml`: Project metadata and dependencies.
- `src/uoa_toolkit/`: Source code for configuration, connectors, joins, exports, and CLI entry point.
- `recipes/`: Example recipes and input data for quick verification.
- `tests/`: Automated tests.

## License

This project is provided as-is for demonstration purposes.
