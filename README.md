# Experimental diffusion coefficients (minerals and silicate melts)

**Pre-release / not published.** Schema v1.0.0. This folder is a GitHub-ready living table: canonical data is CSV, new rows arrive by pull request, and a static page searches the file in the browser. Nothing here is a citable compilation of record.

This is a QA build of 4630 experimental rows (minerals and silicate melts). Most numbers are staged from the 2010 RiMG 72 tables. Do not treat the repo as published, complete, or peer-reviewed.

## Citation

**Citation of record is the row DOI, not this repo.**

Each row points at the experimental paper that produced the calibration (doi, unprefixed 10.). If you use a number, cite that paper. Quote this database only as a finding aid, and still cite the row DOI.

Zhang, Ni and Chen (2010) and Brady and Cherniak (2010) are finding aids. Their chapter DOIs (10.2138/rmg.2010.72.8 and 10.2138/rmg.2010.72.20) must not appear in the doi column. CI rejects them.

**2010 Zhang/Brady numbers are staged** (provenance=compilation_2010 in notes) **pending primary re-extract.** They are a recovery catalog, not a replacement citation. After a PDF pass, ingest a new row (provenance=primary_reextract), mark the staging row quality_flag = superseded, and keep the old record_id (never reuse ids).

## What you can do here

1. **Search** the table in site/ (host, diffusant, type, year, free text).
2. **Add a paper** by appending rows to the CSV and opening a pull request.
3. **QA** with scripts/validate_csv.py (the same check GitHub Actions runs).
4. **Cite** the row primary DOI, not this repository.

GitHub Pages search comes after the first public push. Until then, preview locally (below). Pages is not enabled.

## Layout

- data/diffusion_coefficients.csv: canonical table (append-only record_id)
- schema/schema.csv: header contract, 113 columns
- schema/data_dictionary.md: column meanings, units, controlled vocabularies
- docs/INGEST.md: how to add a row (provenance tokens, units, DOI rules)
- site/index.html: searchable static UI (plain JavaScript, no build step)
- site/data/diffusion_coefficients.csv: copy of the CSV for local and Pages preview
- scripts/validate_csv.py: schema / id / boolean / DOI checker
- .github/workflows/validate.yml: runs the checker on push and pull request
- .github/workflows/pages.yml: placeholder; copies CSV into site/data; does not deploy

## Search the table (local preview)

The page loads data/diffusion_coefficients.csv next to index.html. Opening the HTML as a local file URL often blocks fetch, so serve the site/ folder:

    cd site
    python3 -m http.server 8000

Then open http://127.0.0.1:8000/

Filters: free text, host_type, host_name, diffusant, diffusion_type, year min/max. The grid shows a short column set. Click a row for the rest. DOI cells link to https://doi.org/{doi}.

When Pages is later enabled, set the Pages root to /site. The placeholder workflow already copies the canonical CSV into site/data/ on each build.

## Add a paper (new rows)

1. Read docs/INGEST.md and schema/data_dictionary.md.
2. Take the next unused record_id (DDB + six digits; this QA build ends at DDB004630, so the next id is DDB004631). Never reuse an id. This table is append-only: do not delete or renumber existing rows. Retire a calibration with quality_flag = superseded and a new id.
3. Append one row per published Arrhenius fit (or one isothermal D if there is no fit). Convert to SI; keep the printed number in *_original_* columns.
4. Prefix notes with a provenance token: provenance=post2010_new, provenance=primary_reextract, or provenance=compilation_2010.
5. Put the experimental DOI in doi (not a RiMG chapter).
6. Booleans are lowercase true / false (empty means missing). schema_version is 1.0.0.
7. Open a pull request against this repo. Wait for validate.yml to pass.

Local check before you push:

    python3 scripts/validate_csv.py

CI confirms: 113 columns matching schema/schema.csv, unique record_id, no RiMG compilation DOIs in doi, booleans true/false/empty, and schema_version 1.0.0.

## QA status of this build

- 4630 data rows, 113 columns, schema v1.0.0.
- Five post-2010 draft rows (DDB000001-005, provenance=post2010_new).
- The rest are 2010 Zhang melt tables and Brady mineral rows, staged as compilation_2010, mostly review_status = draft and quality_flag = use_with_caution.
- Empty cells are missing, not zero. No invented D0 / Ea / D.

In scope: laboratory profile or bulk-exchange experiments on mineral hosts and silicate melts/glasses. Out of scope: MD/DFT-only D, natural-zoning inversions, non-silicate liquids. See docs/INGEST.md.

## Remote

Local files only for now. No git remote is configured here. When you are ready, git init, add GitHub as origin, and push. Do not enable Pages until you say go.

