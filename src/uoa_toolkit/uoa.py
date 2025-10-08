"""Unit-of-analysis helpers."""
from __future__ import annotations

from .config import RecipeConfig
from .connectors import load_dataset
from .table import Table


def build_uoa(recipe: RecipeConfig) -> Table:
    """Load the UOA dataset and ensure join keys exist."""

    uoa_dataset = recipe.uoa
    table = load_dataset(uoa_dataset)

    missing_columns = [key for key in uoa_dataset.join_keys if key not in table.columns]
    if missing_columns:
        raise ValueError(f"UOA dataset missing join keys: {missing_columns}")

    if uoa_dataset.select:
        table = table.select(uoa_dataset.select)

    if uoa_dataset.rename:
        table = table.rename(uoa_dataset.rename)

    return table
