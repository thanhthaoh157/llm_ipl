"""Dataset inventory and validation helpers for MGIMO-sourced assets."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

__all__ = ["DatasetSpec", "DatasetReport", "MGIMO_DATASETS", "validate_mgimo_datasets", "summarise_reports"]


@dataclass(frozen=True)
class DatasetSpec:
    """Metadata describing a logical dataset family."""

    slug: str
    title: str
    description: str
    source: str


@dataclass(frozen=True)
class DatasetReport:
    """Validation status for a dataset directory."""

    spec: DatasetSpec
    directory: Path
    directory_exists: bool
    data_files: Sequence[Path]

    @property
    def has_data(self) -> bool:
        return bool(self.data_files)


MGIMO_DATASETS: Sequence[DatasetSpec] = (
    DatasetSpec(
        slug="polity_iv",
        title="Polity IV",
        description="Regime type and characteristics.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_major_power_indicator",
        title="COW Major Power Indicator",
        description="Major power status by country-year.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="archigos",
        title="Archigos",
        description="Political leader tenure and background.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="lead",
        title="LEAD",
        description="Leadership experience and attributes.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_national_capabilities",
        title="COW National Capabilities (CINC)",
        description="Composite index of national capabilities.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="ipe_data_resource",
        title="IPE Data Resource",
        description="Macroeconomic indicators curated by MGIMO.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="historic_bond_yields",
        title="Historic Government Bond Yields",
        description="Sovereign bond yields across the nineteenth and twentieth centuries.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="migration",
        title="Migration",
        description="International migration stocks and flows.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_contiguity",
        title="COW Contiguity",
        description="Direct contiguity relationships between states.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="capital_distance",
        title="Capital-to-Capital Distance",
        description="Great-circle distances between national capitals.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cshapes_distance",
        title="CShapes Minimum Distance",
        description="Minimum border distances from the CShapes dataset.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_interstate_war",
        title="COW Interstate War / IWD",
        description="Interstate war incidence and characteristics.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_intrastate_war",
        title="COW Intrastate War",
        description="Domestic conflict incidence and characteristics.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="prio_intrastate_war",
        title="PRIO Intrastate War",
        description="PRIO conflict dataset for intrastate wars.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="mid",
        title="Militarized Interstate Disputes (MID)",
        description="Militarised dispute events and dyads.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="icb",
        title="International Crisis Behavior (ICB)",
        description="International crisis episodes.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="compellent_threats",
        title="Compellent Threats",
        description="Compellent threat dataset curated by MGIMO.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="icow",
        title="Issue Correlates of War (ICOW)",
        description="Territorial and other issue disputes.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="terrorism_incidents",
        title="Terrorism Incidents",
        description="Aggregated terrorism indicators.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="atop_alliances",
        title="ATOP Alliances",
        description="Alliance membership records.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="cow_alliances",
        title="COW Alliances",
        description="Correlates of War alliance data.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="igo_memberships",
        title="IGO Memberships",
        description="Governmental organisation memberships.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="joint_igo_memberships",
        title="Joint IGO Memberships",
        description="Dyadic counts of shared IGO memberships.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="s_similarity",
        title="S-score",
        description="Foreign policy similarity scores (S).",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="tau_b_similarity",
        title="Tau-b",
        description="Kendall's tau-b foreign policy similarity.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="nuclear_deployments",
        title="Nuclear Deployments",
        description="Indicators of deployed nuclear capabilities.",
        source="https://mgimo.ru/",
    ),
    DatasetSpec(
        slug="nuclear_cooperation",
        title="Nuclear Cooperation Agreements",
        description="Catalogue of nuclear cooperation treaties.",
        source="https://mgimo.ru/",
    ),
)

_VALID_SUFFIXES = {".csv", ".tsv", ".txt", ".parquet", ".feather", ".dta", ".sav", ".xlsx", ".xls"}


def _iter_data_files(directory: Path) -> Sequence[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    files = [
        item
        for item in directory.iterdir()
        if item.is_file() and item.suffix.lower() in _VALID_SUFFIXES
    ]
    return sorted(files)


def validate_mgimo_datasets(
    base_dir: Path,
    *,
    create_dirs: bool = False,
    specs: Iterable[DatasetSpec] = MGIMO_DATASETS,
) -> Sequence[DatasetReport]:
    """Validate that the expected MGIMO dataset folders exist and contain data files."""

    base_dir = base_dir.expanduser()
    if create_dirs:
        base_dir.mkdir(parents=True, exist_ok=True)

    reports: list[DatasetReport] = []
    for spec in specs:
        dataset_dir = base_dir / spec.slug
        if create_dirs and not dataset_dir.exists():
            dataset_dir.mkdir(parents=True, exist_ok=True)
        data_files = _iter_data_files(dataset_dir)
        reports.append(
            DatasetReport(
                spec=spec,
                directory=dataset_dir,
                directory_exists=dataset_dir.exists(),
                data_files=tuple(data_files),
            )
        )
    return tuple(reports)


def summarise_reports(
    reports: Sequence[DatasetReport],
) -> tuple[Sequence[DatasetReport], Sequence[DatasetReport]]:
    """Return lists of missing directories and empty directories."""

    missing = [report for report in reports if not report.directory_exists]
    empty = [report for report in reports if report.directory_exists and not report.has_data]
    return tuple(missing), tuple(empty)
