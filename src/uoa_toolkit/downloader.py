"""Dataset download helpers for publicly available political science sources."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

try:  # pragma: no cover - exercised when httpx is available
    import httpx
except ModuleNotFoundError:  # pragma: no cover - exercised in constrained environments
    import types
    import urllib.request

    class _SimpleResponse:
        def __init__(self, content: bytes):
            self.content = content

        def raise_for_status(self) -> None:
            return

    class _SimpleClient:
        def __init__(self, *_, **__):
            pass

        def get(self, url: str):
            try:
                with urllib.request.urlopen(url) as handle:  # nosec - official sources
                    return _SimpleResponse(handle.read())
            except Exception as error:  # pragma: no cover - network errors
                raise RuntimeError(str(error)) from error

        def close(self) -> None:
            return

    httpx = types.SimpleNamespace(  # type: ignore[assignment]
        Client=_SimpleClient,
        HTTPError=RuntimeError,
    )

__all__ = [
    "RemoteDataset",
    "REMOTE_DATASETS",
    "DownloadError",
    "resolve_dataset",
    "list_datasets",
    "download_dataset",
    "download_datasets",
    "generate_python_snippet",
]


@dataclass(frozen=True)
class RemoteDataset:
    """Description of a downloadable dataset."""

    slug: str
    title: str
    description: str
    landing_page: str
    download_url: str | None = None
    filename: str | None = None
    notes: str | None = None
    requires_manual_steps: bool = False

    def supports_automation(self) -> bool:
        """Return True when the dataset exposes a direct download URL."""

        return not self.requires_manual_steps and bool(self.download_url)


class DownloadError(RuntimeError):
    """Raised when a dataset could not be downloaded."""


REMOTE_DATASETS: Sequence[RemoteDataset] = (
    RemoteDataset(
        slug="polity_iv",
        title="Polity5 Annual Time-Series, 1946-2018",
        description="Regime type and authority characteristics for sovereign states.",
        landing_page="https://www.systemicpeace.org/polityproject.html",
        download_url="https://www.systemicpeace.org/inscr/p5v2018.xls",
        filename="polity5_annual.xls",
        notes="Latest public release covering 1946-2018.",
    ),
    RemoteDataset(
        slug="cow_major_power_indicator",
        title="Correlates of War State System Membership",
        description="Includes the major power classification for recognised states.",
        landing_page="https://correlatesofwar.org/data-sets/state-system-membership/",
        download_url="https://correlatesofwar.org/wp-content/uploads/state_system_membership.zip",
        filename="state_system_membership.zip",
        notes="ZIP archive containing CSV and documentation files.",
    ),
    RemoteDataset(
        slug="archigos",
        title="Archigos: A Database on Leaders",
        description="Political leaders and tenure characteristics since 1875.",
        landing_page="https://www.rochester.edu/college/faculty/hgoemans/data.htm",
        download_url="https://www.rochester.edu/college/faculty/hgoemans/Archigos/Archigos_4.1.zip",
        filename="archigos_4_1.zip",
    ),
    RemoteDataset(
        slug="lead",
        title="Leadership Experience and Attributes Database (LEAD)",
        description="Leader background and experience traits.",
        landing_page="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/SYZZEY",
        download_url=(
            "https://dataverse.harvard.edu/api/access/datafile/6182606?format=original"
        ),
        filename="lead_dataset.csv",
        notes="Direct download via Harvard Dataverse API.",
    ),
    RemoteDataset(
        slug="cow_national_capabilities",
        title="Correlates of War National Material Capabilities",
        description="Composite Index of National Capability (CINC).",
        landing_page="https://correlatesofwar.org/data-sets/national-material-capabilities/",
        download_url="https://correlatesofwar.org/wp-content/uploads/NMC-data-1816-2016-v6.zip",
        filename="nmc_v6.zip",
    ),
    RemoteDataset(
        slug="ipe_data_resource",
        title="International Political Economy Data Resource",
        description="Macroeconomic indicators curated by the IPE Data Resource project.",
        landing_page="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X093TV",
        download_url="https://dataverse.harvard.edu/api/access/datafile/6020288?format=original",
        filename="ipe_data_resource.zip",
    ),
    RemoteDataset(
        slug="historic_bond_yields",
        title="Jorda-Schularick-Taylor Macrohistory Database",
        description="Long-run macro-financial series including sovereign yields.",
        landing_page="https://www.macrohistory.net/database/",
        download_url="https://www.macrohistory.net/app/download/7247271057/MHDB_Data_Full.zip",
        filename="macrohistory_full.zip",
        notes="Archive includes government bond yields among other indicators.",
    ),
    RemoteDataset(
        slug="migration",
        title="World Bank Global Bilateral Migration Database",
        description="Bilateral migrant stock estimates for 1960-2000.",
        landing_page="https://databank.worldbank.org/source/global-bilateral-migration",
        download_url="https://databankfiles.worldbank.org/public/ddpext_download/GBMD/CSV.zip",
        filename="global_bilateral_migration.zip",
    ),
    RemoteDataset(
        slug="cow_contiguity",
        title="Correlates of War Direct Contiguity",
        description="Direct land and sea contiguity relationships among states.",
        landing_page="https://correlatesofwar.org/data-sets/direct-contiguity/",
        download_url="https://correlatesofwar.org/wp-content/uploads/DirectContiguity320.zip",
        filename="cow_contiguity_v3_2.zip",
    ),
    RemoteDataset(
        slug="capital_distance",
        title="CEPII GeoDist Capital Distances",
        description="Great-circle distances between national capitals.",
        landing_page="https://www.cepii.fr/cepii/en/bdd_modele/bdd_modele_item.asp?id=6",
        download_url="https://www.cepii.fr/DATA_DOWNLOAD/geodist/GeoDist_CSV.zip",
        filename="geodist_csv.zip",
    ),
    RemoteDataset(
        slug="cshapes_distance",
        title="CShapes Minimum Distance",
        description="Annualised minimum distances derived from historical borders.",
        landing_page="https://icr.ethz.ch/data/cshapes/shapefile.html",
        download_url="https://dataverse.harvard.edu/api/access/datafile/6159312?format=original",
        filename="cshapes_distances.zip",
    ),
    RemoteDataset(
        slug="cow_interstate_war",
        title="Correlates of War Interstate War",
        description="Interstate war onsets and battle deaths.",
        landing_page="https://correlatesofwar.org/data-sets/cow-war/",
        download_url="https://correlatesofwar.org/wp-content/uploads/COW-war.zip",
        filename="cow_interstate_war.zip",
    ),
    RemoteDataset(
        slug="cow_intrastate_war",
        title="Correlates of War Intrastate War",
        description="Civil war conflict listings and characteristics.",
        landing_page="https://correlatesofwar.org/data-sets/cow-war/",
        download_url="https://correlatesofwar.org/wp-content/uploads/COW-civil-war.zip",
        filename="cow_intrastate_war.zip",
    ),
    RemoteDataset(
        slug="prio_intrastate_war",
        title="UCDP/PRIO Armed Conflict Dataset",
        description="Armed conflict dyads and country-years, 1946-2022.",
        landing_page="https://ucdp.uu.se/downloads/",
        download_url="https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-221.zip",
        filename="ucdp_prio_acd_221.zip",
    ),
    RemoteDataset(
        slug="mid",
        title="Militarized Interstate Disputes (MID5)",
        description="Dyadic militarised disputes between states.",
        landing_page="https://correlatesofwar.org/data-sets/mids/",
        download_url="https://correlatesofwar.org/wp-content/uploads/MIDB_5.0_csv.zip",
        filename="mid5_csv.zip",
    ),
    RemoteDataset(
        slug="icb",
        title="International Crisis Behavior (ICB) Project",
        description="International crisis episodes, 1918-2021.",
        landing_page="https://sites.duke.edu/icbdata/",
        download_url="https://sites.duke.edu/icbdata/files/2022/06/ICB-Project-Data-V16.zip",
        filename="icb_v16.zip",
    ),
    RemoteDataset(
        slug="compellent_threats",
        title="Militarized Compellent Threats",
        description="Compellent threat episodes and outcomes.",
        landing_page="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VDJQ1E",
        download_url="https://dataverse.harvard.edu/api/access/datafile/6173677?format=original",
        filename="compellent_threats.csv",
    ),
    RemoteDataset(
        slug="icow",
        title="Issue Correlates of War (ICOW)",
        description="Territorial, maritime, and river claims data.",
        landing_page="https://data.icow.org/",
        download_url="https://data.icow.org/data/ICOW_Dataset_2022_1.zip",
        filename="icow_dataset_2022_1.zip",
    ),
    RemoteDataset(
        slug="terrorism_incidents",
        title="Global Terrorism Database (GTD)",
        description="Worldwide terrorism incidents with casualties and attributes.",
        landing_page="https://www.start.umd.edu/gtd-download",
        notes="Requires registration and licence acceptance; no direct download provided.",
        requires_manual_steps=True,
    ),
    RemoteDataset(
        slug="atop_alliances",
        title="Alliance Treaty Obligations and Provisions (ATOP)",
        description="Alliance membership, obligations, and texts.",
        landing_page="https://www.atopdata.org/data.html",
        download_url="https://www.atopdata.org/uploads/1/2/5/4/125471701/atop_dyadic_v5_1.zip",
        filename="atop_dyadic_v5_1.zip",
    ),
    RemoteDataset(
        slug="cow_alliances",
        title="Correlates of War Formal Alliances",
        description="Formal alliance membership indicators.",
        landing_page="https://correlatesofwar.org/data-sets/formal-alliances/",
        download_url="https://correlatesofwar.org/wp-content/uploads/alliance_v4.1_by_membership_yearly.zip",
        filename="cow_alliances_v4_1.zip",
    ),
    RemoteDataset(
        slug="igo_memberships",
        title="Correlates of War Intergovernmental Organizations",
        description="IGO membership by state-year.",
        landing_page="https://correlatesofwar.org/data-sets/igos/",
        download_url="https://correlatesofwar.org/wp-content/uploads/COW-IGO.zip",
        filename="cow_igo.zip",
    ),
    RemoteDataset(
        slug="joint_igo_memberships",
        title="Correlates of War Joint IGO Memberships",
        description="Dyadic counts of shared IGO participation.",
        landing_page="https://correlatesofwar.org/data-sets/igos/",
        download_url="https://correlatesofwar.org/wp-content/uploads/IGOdyad_v3.0.zip",
        filename="cow_joint_igo_v3.zip",
    ),
    RemoteDataset(
        slug="s_similarity",
        title="Affinity of Nations (S-scores)",
        description="Foreign policy similarity based on UN General Assembly voting.",
        landing_page="https://pages.ucsd.edu/~egartzke/datasets.htm",
        download_url="https://pages.ucsd.edu/~egartzke/dyadyears/affinity_2014.zip",
        filename="affinity_2014.zip",
    ),
    RemoteDataset(
        slug="tau_b_similarity",
        title="UN Voting Ideal Points (Bailey-Strezhnev-Voeten)",
        description="Kendall tau-b similarity scores derived from UN voting ideal points.",
        landing_page="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LEJUQZ",
        download_url="https://dataverse.harvard.edu/api/access/datafile/2445513?format=original",
        filename="un_ideal_points.dta",
    ),
    RemoteDataset(
        slug="nuclear_deployments",
        title="Strategic Nuclear Forces Dataset",
        description="Deployable nuclear warheads by country-year.",
        landing_page="https://ourworldindata.org/grapher/estimated-nuclear-warheads-deliverable-in-first-strike",
        download_url="https://ourworldindata.org/grapher/estimated-nuclear-warheads-deliverable-in-first-strike.csv",
        filename="strategic_nuclear_forces.csv",
    ),
    RemoteDataset(
        slug="nuclear_cooperation",
        title="Nuclear Cooperation Agreements Dataset",
        description="Bilateral nuclear cooperation treaties and characteristics.",
        landing_page="https://www.matthewfuhrmann.com/datasets.html",
        download_url="https://static1.squarespace.com/static/5b1f6a9d1aef1d54209b7888/t/6615f31bcfaad27992215487/1712692764876/Nuclear+Cooperation+Agreement+Dataset+%28v.2024%29.xlsx",
        filename="nuclear_cooperation_agreements_2024.xlsx",
    ),
)


def _dataset_index() -> Mapping[str, RemoteDataset]:
    return {dataset.slug: dataset for dataset in REMOTE_DATASETS}


def resolve_dataset(slug: str) -> RemoteDataset:
    """Return dataset metadata for a slug, raising if it is unknown."""

    datasets = _dataset_index()
    try:
        return datasets[slug]
    except KeyError as error:  # pragma: no cover - defensive branch
        raise KeyError(f"Unknown dataset slug: {slug}") from error


def list_datasets() -> Sequence[RemoteDataset]:
    """Return all known dataset specifications."""

    return REMOTE_DATASETS


def _target_filename(dataset: RemoteDataset) -> str:
    if dataset.filename:
        return dataset.filename
    if dataset.download_url:
        return Path(dataset.download_url).name or f"{dataset.slug}.dat"
    return f"{dataset.slug}.dat"


def download_dataset(
    slug: str,
    target_root: Path,
    *,
    overwrite: bool = False,
    client: httpx.Client | None = None,
) -> Path:
    """Download a dataset identified by ``slug`` into ``target_root``."""

    dataset = resolve_dataset(slug)
    if not dataset.supports_automation():
        message = (
            f"Dataset '{dataset.slug}' requires manual download via {dataset.landing_page}."
        )
        raise DownloadError(message)

    target_root = target_root.expanduser().resolve()
    dataset_dir = target_root / dataset.slug
    dataset_dir.mkdir(parents=True, exist_ok=True)

    filename = _target_filename(dataset)
    destination = dataset_dir / filename
    if destination.exists() and not overwrite:
        return destination

    own_client = False
    if client is None:
        client = httpx.Client(follow_redirects=True, timeout=120.0)
        own_client = True

    try:
        response = client.get(dataset.download_url)  # type: ignore[arg-type]
        response.raise_for_status()
    except httpx.HTTPError as error:  # pragma: no cover - exercised via tests
        raise DownloadError(
            f"Failed to download {dataset.title} from {dataset.download_url}: {error}"
        ) from error
    finally:
        if own_client:
            client.close()

    with destination.open("wb") as handle:
        handle.write(response.content)

    return destination


def download_datasets(
    slugs: Iterable[str],
    target_root: Path,
    *,
    overwrite: bool = False,
    client: httpx.Client | None = None,
) -> Mapping[str, Path]:
    """Download multiple datasets and return a slug→path mapping."""

    results: dict[str, Path] = {}
    for slug in slugs:
        path = download_dataset(slug, target_root, overwrite=overwrite, client=client)
        results[slug] = path
    return results


def generate_python_snippet(slugs: Sequence[str], target_root: Path) -> str:
    """Return a ready-to-run Python snippet for downloading datasets."""

    formatted_slugs = ", ".join(repr(slug) for slug in slugs)
    snippet = f"""from pathlib import Path\nfrom uoa_toolkit.downloader import download_datasets\n\nbase_dir = Path(r"{str(target_root)}")\nbase_dir.mkdir(parents=True, exist_ok=True)\nresults = download_datasets([{formatted_slugs}], base_dir)\nfor slug, path in results.items():\n    print(f"{{slug}} -> {{path}}")\n"""
    return snippet
