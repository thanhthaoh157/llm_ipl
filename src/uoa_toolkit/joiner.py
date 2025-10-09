"""Join logic for combining datasets into a panel."""
from __future__ import annotations

from typing import Iterable, Sequence

from .config import DatasetConfig, RecipeConfig
from .connectors import load_dataset
from .table import Table
from .uoa import build_uoa


def _prepare_columns(table: Table, dataset: DatasetConfig) -> Table:
    if dataset.select:
        table = table.select(dataset.select)

    if dataset.rename:
        table = table.rename(dataset.rename)

    if dataset.prefix:
        key_columns: Sequence[str] = list(dataset.join_keys)
        timestamp = dataset.timestamp_column
        key_columns = list(key_columns) + ([timestamp] if timestamp else [])
        rename_map = {
            column: f"{dataset.prefix}{column}"
            for column in table.columns
            if column not in key_columns
        }
        table = table.rename(rename_map)

    return table


def _join_asof(base: Table, other: Table, dataset: DatasetConfig) -> Table:
    if not dataset.timestamp_column:
        raise ValueError("timestamp_column must be provided for as-of joins")

    timestamp = dataset.timestamp_column
    if timestamp not in base.columns:
        raise ValueError(f"Base table missing timestamp column '{timestamp}' for as-of join")
    if timestamp not in other.columns:
        raise ValueError(f"Joined table missing timestamp column '{timestamp}' for as-of join")

    by = dataset.join_keys or None
    return base.join_asof(other, timestamp=timestamp, by=by)


def _join_left(base: Table, other: Table, dataset: DatasetConfig) -> Table:
    if not dataset.join_keys:
        raise ValueError("Left join requires join_keys to be specified")
    return base.join_left(other, dataset.join_keys)


def join_datasets(base: Table, datasets: Iterable[DatasetConfig]) -> Table:
    """Iteratively join datasets onto the base table."""

    joined = base
    for dataset in datasets:
        other = load_dataset(dataset)
        other = _prepare_columns(other, dataset)
        if dataset.timestamp_column:
            joined = _join_asof(joined, other, dataset)
        else:
            joined = _join_left(joined, other, dataset)
    return joined


def build_panel(recipe: RecipeConfig) -> Table:
    """Build the final panel according to the recipe."""

    base = build_uoa(recipe)
    base = _prepare_columns(base, recipe.uoa)
    return join_datasets(base, recipe.datasets)
