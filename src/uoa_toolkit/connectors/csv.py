"""CSV connector implementation."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..config import CSVConnectorConfig
from ..table import Table


def load_csv(config: CSVConnectorConfig) -> Table:
    """Load a CSV file into a Table."""

    return Table.read_csv(
        Path(config.path),
        has_header=config.has_header,
        delimiter=config.delimiter,
    )


def sample_csv(path: Path, n_rows: int = 5) -> Optional[Table]:
    """Return a sample of the CSV file for manifest previews."""

    if not Path(path).exists():
        return None

    table = Table.read_csv(Path(path))
    return Table.from_rows(table.rows[:n_rows], table.columns)
