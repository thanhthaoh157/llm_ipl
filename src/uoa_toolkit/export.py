"""Export utilities for panel datasets."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .manifest import ManifestEntry
from .table import Table, write_xlsx


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def export_excel(
    table: Table,
    dictionary: Table,
    manifest_entries: List[ManifestEntry],
    metadata: Table,
    output_path: Path,
) -> None:
    """Export panel, dictionary, and manifest metadata to an Excel workbook."""

    _ensure_directory(output_path.parent)

    sources_table = Table.from_rows(
        [
            {"name": entry.name, "source": entry.source, "description": entry.description}
            for entry in manifest_entries
        ],
        columns=["name", "source", "description"],
    )

    sheets = {
        "panel": table,
        "dictionary": dictionary,
        "manifest": metadata,
        "sources": sources_table,
    }
    write_xlsx(output_path, sheets)


def export_flat(table: Table, output_path: Path, format: str) -> None:
    """Export the panel to CSV or Parquet."""

    _ensure_directory(output_path.parent)
    if format == "csv":
        table.write_csv(output_path)
    elif format == "parquet":
        table.write_parquet(output_path)
    else:  # pragma: no cover - guarded by caller
        raise ValueError(f"Unsupported format: {format}")


def export_outputs(
    table: Table,
    dictionary: Table,
    manifest_entries: List[ManifestEntry],
    metadata: Table,
    output_directory: Path,
    base_file_name: str,
    formats: List[str],
) -> Dict[str, Path]:
    """Export all requested artefacts and return their paths."""

    output_directory = output_directory.resolve()
    _ensure_directory(output_directory)

    exported: Dict[str, Path] = {}

    if "excel" in formats:
        excel_path = output_directory / base_file_name
        if not excel_path.suffix:
            excel_path = excel_path.with_suffix(".xlsx")
        export_excel(table, dictionary, manifest_entries, metadata, excel_path)
        exported["excel"] = excel_path

    if "csv" in formats:
        csv_path = output_directory / (Path(base_file_name).stem + ".csv")
        export_flat(table, csv_path, "csv")
        exported["csv"] = csv_path

    if "parquet" in formats:
        parquet_path = output_directory / (Path(base_file_name).stem + ".parquet")
        export_flat(table, parquet_path, "parquet")
        exported["parquet"] = parquet_path

    return exported
