"""Configuration models for recipe-driven panel construction."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class CSVConnectorConfig:
    type: str = "csv"
    path: Path = Path()
    infer_schema_length: Optional[int] = None
    has_header: bool = True
    delimiter: str = ","

    @classmethod
    def from_dict(cls, data: Dict, base_dir: Path) -> "CSVConnectorConfig":
        path = Path(data.get("path", "")).expanduser()
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        return cls(
            path=path,
            infer_schema_length=data.get("infer_schema_length"),
            has_header=data.get("has_header", True),
            delimiter=data.get("delimiter", ","),
        )


ConnectorConfig = CSVConnectorConfig


@dataclass
class DatasetConfig:
    name: str
    connector: ConnectorConfig
    join_keys: List[str] = field(default_factory=list)
    timestamp_column: Optional[str] = None
    select: Optional[List[str]] = None
    rename: Dict[str, str] = field(default_factory=dict)
    prefix: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict, base_dir: Path) -> "DatasetConfig":
        connector_data = data.get("connector", {})
        connector_type = connector_data.get("type", "csv")
        if connector_type != "csv":
            raise ValueError(f"Unsupported connector type: {connector_type}")
        connector = CSVConnectorConfig.from_dict(connector_data, base_dir)
        return cls(
            name=data["name"],
            connector=connector,
            join_keys=list(data.get("join_keys", [])),
            timestamp_column=data.get("timestamp_column"),
            select=list(data.get("select", [])) if data.get("select") else None,
            rename=dict(data.get("rename", {})),
            prefix=data.get("prefix"),
        )


@dataclass
class OutputConfig:
    directory: Path = Path("output")
    file_name: str = "panel.xlsx"
    formats: List[str] = field(default_factory=lambda: ["excel"])

    @classmethod
    def from_dict(cls, data: Dict, base_dir: Path) -> "OutputConfig":
        directory = Path(data.get("directory", "output")).expanduser()
        if not directory.is_absolute():
            directory = (base_dir / directory).resolve()
        return cls(
            directory=directory,
            file_name=data.get("file_name", "panel.xlsx"),
            formats=list(data.get("formats", ["excel"])),
        )


@dataclass
class RecipeConfig:
    name: str
    description: Optional[str]
    uoa: DatasetConfig
    datasets: List[DatasetConfig]
    output: OutputConfig

    @classmethod
    def from_dict(cls, data: Dict, base_dir: Path) -> "RecipeConfig":
        uoa = DatasetConfig.from_dict(data["uoa"], base_dir)
        datasets = [DatasetConfig.from_dict(item, base_dir) for item in data.get("datasets", [])]
        output = OutputConfig.from_dict(data.get("output", {}), base_dir)
        return cls(
            name=data["name"],
            description=data.get("description"),
            uoa=uoa,
            datasets=datasets,
            output=output,
        )


def load_recipe(path: Path) -> RecipeConfig:
    """Load a recipe configuration from a YAML file."""

    path = Path(path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle.read())

    return RecipeConfig.from_dict(raw, path.parent)
