"""Connector registry."""
from __future__ import annotations

from ..config import CSVConnectorConfig, DatasetConfig
from ..table import Table
from . import csv as csv_connector


def load_dataset(dataset: DatasetConfig) -> Table:
    """Load a dataset according to its connector configuration."""

    connector = dataset.connector
    if isinstance(connector, CSVConnectorConfig):
        return csv_connector.load_csv(connector)

    raise ValueError(f"Unsupported connector type: {type(connector)!r}")


def sample_dataset(dataset: DatasetConfig, n_rows: int = 5) -> Table | None:
    """Return a small sample of the dataset for manifest documentation."""

    connector = dataset.connector
    if isinstance(connector, CSVConnectorConfig):
        return csv_connector.sample_csv(connector.path, n_rows=n_rows)

    return None
