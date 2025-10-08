# MGIMO Dataset Workspace

The repository does not bundle the MGIMO-hosted datasets referenced in the real-world
panel requests because they are large, frequently updated, and may be subject to
licensing restrictions. Instead, the toolkit now reserves the `data/mgimo/` directory
as a staging area where you can place officially downloaded files.

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

| Slug | Dataset | Summary |
| --- | --- | --- |
| `polity_iv` | Polity IV | Regime type and characteristics. |
| `cow_major_power_indicator` | COW Major Power Indicator | Country major power status by year. |
| `archigos` | Archigos | Political leader tenure and background. |
| `lead` | LEAD | Leadership experience and attributes. |
| `cow_national_capabilities` | COW National Capabilities (CINC) | Composite index of national capabilities. |
| `ipe_data_resource` | IPE Data Resource | Macroeconomic indicators curated by MGIMO. |
| `historic_bond_yields` | Historic Government Bond Yields | Sovereign bond yields across the 19th–20th centuries. |
| `migration` | Migration | Bilateral migration stock and flow data. |
| `cow_contiguity` | COW Contiguity | Interstate contiguity relationships. |
| `capital_distance` | Capital-to-Capital Distance | Great-circle distances between national capitals. |
| `cshapes_distance` | CShapes Minimum Distance | Minimum distances between state borders. |
| `cow_interstate_war` | COW Interstate War / IWD | Interstate war incidence and attributes. |
| `cow_intrastate_war` | COW Intrastate War | Domestic conflict incidence and characteristics. |
| `prio_intrastate_war` | PRIO Intrastate War | PRIO conflict dataset for intrastate wars. |
| `mid` | Militarized Interstate Disputes (MID) | Militarized dispute events and dyads. |
| `icb` | International Crisis Behavior (ICB) | International crisis episodes. |
| `compellent_threats` | Compellent Threats | Compellent threat dataset curated by MGIMO. |
| `icow` | Issue Correlates of War (ICOW) | Territorial and other issue disputes. |
| `terrorism_incidents` | Terrorism Incidents | Aggregated terrorism indicators. |
| `atop_alliances` | ATOP Alliances | Alliance membership records. |
| `cow_alliances` | COW Alliances | Correlates of War alliance data. |
| `igo_memberships` | IGO Memberships | Membership rosters for intergovernmental organisations. |
| `joint_igo_memberships` | Joint IGO Memberships | Dyadic counts of shared IGO memberships. |
| `s_similarity` | S-score | Foreign policy similarity scores. |
| `tau_b_similarity` | Tau-b | Kendall's tau-b foreign policy alignment. |
| `nuclear_deployments` | Nuclear Deployments | Indicators of deployed nuclear capabilities. |
| `nuclear_cooperation` | Nuclear Cooperation Agreements | Catalog of nuclear cooperation treaties. |

Refer to the MGIMO data portal (https://mgimo.ru/) for authoritative download links
and licensing terms. Populate the directories with the original files (unzipped where
applicable) to keep the recipe connectors simple.

Once populated, you can craft a recipe that points to the files within `data/mgimo/`
and execute it with the standard `run` command.
