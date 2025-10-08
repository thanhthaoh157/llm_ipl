"""Manifest generation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from .config import DatasetConfig, RecipeConfig
from .connectors import sample_dataset
from .table import Table


@dataclass
class ManifestEntry:
    name: str
    source: str
    description: str


def dataset_to_entry(dataset: DatasetConfig) -> ManifestEntry:
    connector = dataset.connector
    if hasattr(connector, "path"):
        source = str(getattr(connector, "path"))
    else:
        source = dataset.name

    description = "As-of join" if dataset.timestamp_column else "Left join"
    return ManifestEntry(name=dataset.name, source=source, description=description)


def build_manifest(recipe: RecipeConfig, final_table: Table) -> Dict[str, object]:
    """Build manifest artefacts for the exported panel."""

    entries = [dataset_to_entry(recipe.uoa)] + [dataset_to_entry(ds) for ds in recipe.datasets]

    dictionary = Table.from_rows(
        [
            {"column": column, "dtype": dtype}
            for column, dtype in final_table.schema.items()
        ],
        columns=["column", "dtype"],
    )

    samples = {
        entry.name: sample_dataset(dataset)
        for entry, dataset in zip(entries, [recipe.uoa, *recipe.datasets], strict=False)
    }

    metadata = Table.from_rows(
        [
            {
                "name": recipe.name,
                "generated_at": datetime.utcnow().isoformat(),
                "description": recipe.description or "",
                "row_count": final_table.height,
                "column_count": final_table.width,
            }
        ],
        columns=["name", "generated_at", "description", "row_count", "column_count"],
    )

    return {
        "entries": entries,
        "dictionary": dictionary,
        "samples": samples,
        "metadata": metadata,
    }
