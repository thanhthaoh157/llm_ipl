# MGIMO Dataset Workspace

The repository does not bundle the MGIMO-hosted datasets referenced in the real-world
panel requests because they are large, frequently updated, and may be subject to
licensing restrictions. Instead, the toolkit now reserves the `data/mgimo/` directory
as a staging area where you can place officially downloaded files.

Run the downloader to pull every dataset with a direct download URL into this
directory:

```bash
python -m uoa_toolkit.cli download-datasets
```

Append `--emit-code` to print a Python snippet that invokes the same helper from your
own scripts. Datasets that require manual steps (for example, licence acceptance) are
flagged during the run; visit the landing page listed below and place the files in the
matching subdirectory when done.

Use the CLI helper to scaffold the directory layout and validate that the downloads
are present before running recipes:

```bash
python -m uoa_toolkit.cli validate-mgimo data/mgimo --create-dirs
```

With `--create-dirs`, the command will materialise the expected subfolders for each
MGIMO dataset family. It will then report which datasets are still missing files. If
you have already downloaded the data, place the relevant CSV/TSV/Parquet/Excel files
into the matching directory and re-run the command. When all directories contain
recognised files, the command exits successfully.

The datasets requested by the user include (slugs match the subdirectory names):

| Slug | Dataset | Summary | Landing page | Auto download? |
| --- | --- | --- | --- | --- |
| `polity_iv` | Polity IV | Regime type and characteristics. | <https://www.systemicpeace.org/polityproject.html> | ✅ |
| `cow_major_power_indicator` | COW Major Power Indicator | Country major power status by year. | <https://correlatesofwar.org/data-sets/state-system-membership/> | ✅ |
| `archigos` | Archigos | Political leader tenure and background. | <https://www.rochester.edu/college/faculty/hgoemans/data.htm> | ✅ |
| `lead` | LEAD | Leadership experience and attributes. | <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/SYZZEY> | ✅ |
| `cow_national_capabilities` | COW National Capabilities (CINC) | Composite index of national capabilities. | <https://correlatesofwar.org/data-sets/national-material-capabilities/> | ✅ |
| `ipe_data_resource` | IPE Data Resource | Macroeconomic indicators curated by MGIMO. | <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X093TV> | ✅ |
| `historic_bond_yields` | Historic Government Bond Yields | Sovereign bond yields across the 19th–20th centuries. | <https://www.macrohistory.net/database/> | ✅ |
| `migration` | Migration | Bilateral migration stock and flow data. | <https://databank.worldbank.org/source/global-bilateral-migration> | ✅ |
| `cow_contiguity` | COW Contiguity | Interstate contiguity relationships. | <https://correlatesofwar.org/data-sets/direct-contiguity/> | ✅ |
| `capital_distance` | Capital-to-Capital Distance | Great-circle distances between national capitals. | <https://www.cepii.fr/cepii/en/bdd_modele/bdd_modele_item.asp?id=6> | ✅ |
| `cshapes_distance` | CShapes Minimum Distance | Minimum distances between state borders. | <https://icr.ethz.ch/data/cshapes/shapefile.html> | ✅ |
| `cow_interstate_war` | COW Interstate War / IWD | Interstate war incidence and attributes. | <https://correlatesofwar.org/data-sets/cow-war/> | ✅ |
| `cow_intrastate_war` | COW Intrastate War | Domestic conflict incidence and characteristics. | <https://correlatesofwar.org/data-sets/cow-war/> | ✅ |
| `prio_intrastate_war` | PRIO Intrastate War | PRIO conflict dataset for intrastate wars. | <https://ucdp.uu.se/downloads/> | ✅ |
| `mid` | Militarized Interstate Disputes (MID) | Militarized dispute events and dyads. | <https://correlatesofwar.org/data-sets/mids/> | ✅ |
| `icb` | International Crisis Behavior (ICB) | International crisis episodes. | <https://sites.duke.edu/icbdata/> | ✅ |
| `compellent_threats` | Compellent Threats | Compellent threat dataset curated by MGIMO. | <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VDJQ1E> | ✅ |
| `icow` | Issue Correlates of War (ICOW) | Territorial and other issue disputes. | <https://data.icow.org/> | ✅ |
| `terrorism_incidents` | Terrorism Incidents | Aggregated terrorism indicators. | <https://www.start.umd.edu/gtd-download> | ⚠️ Manual (accept licence) |
| `atop_alliances` | ATOP Alliances | Alliance membership records. | <https://www.atopdata.org/data.html> | ✅ |
| `cow_alliances` | COW Alliances | Correlates of War alliance data. | <https://correlatesofwar.org/data-sets/formal-alliances/> | ✅ |
| `igo_memberships` | IGO Memberships | Membership rosters for intergovernmental organisations. | <https://correlatesofwar.org/data-sets/igos/> | ✅ |
| `joint_igo_memberships` | Joint IGO Memberships | Dyadic counts of shared IGO memberships. | <https://correlatesofwar.org/data-sets/igos/> | ✅ |
| `s_similarity` | S-score | Foreign policy similarity scores. | <https://pages.ucsd.edu/~egartzke/datasets.htm> | ✅ |
| `tau_b_similarity` | Tau-b | Kendall's tau-b foreign policy alignment. | <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LEJUQZ> | ✅ |
| `nuclear_deployments` | Nuclear Deployments | Indicators of deployed nuclear capabilities. | <https://ourworldindata.org/grapher/estimated-nuclear-warheads-deliverable-in-first-strike> | ✅ |
| `nuclear_cooperation` | Nuclear Cooperation Agreements | Catalog of nuclear cooperation treaties. | <https://www.matthewfuhrmann.com/datasets.html> | ✅ |

Refer to the MGIMO data portal (https://mgimo.ru/) for authoritative download links
and licensing terms. Populate the directories with the original files (unzipped where
applicable) to keep the recipe connectors simple.

Once populated, you can craft a recipe that points to the files within `data/mgimo/`
and execute it with the standard `run` command.
