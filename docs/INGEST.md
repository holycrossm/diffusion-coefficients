# First-ingest protocol (schema v1.0.0)

This database is a **living public update** of the 2010 RiMG 72 compilations: Zhang, Ni & Chen (2010) for melts and Brady & Cherniak (2010) for minerals. The 2010 tables are **v0 baseline** to recover and extend, not something to ignore. Wave-1 work is (a) recover those tables as a staged catalog, then (b) add 2011–2026 primary experiments those compilations miss.

**Citation of record is always the primary experimental paper** (`doi` = that paper’s unprefixed `10.…`). The 2010 compilation is provenance, not a substitute citation.

Missing cells are empty. Booleans are `true`/`false`. `schema_version` is always `1.0.0`. Assign `record_id` as `DDB` + six digits, never reused.

---

## 0. Provenance (mandatory)

v1.0.0 has no dedicated column. Put a **first tagged token in `notes`**:

```
provenance=compilation_2010
provenance=primary_reextract
provenance=post2010_new
```

| Token | Meaning |
|---|---|
| `compilation_2010` | Numbers staged from a 2010 RiMG table (Zhang Ch. 8 xls, Brady catalog, Baxter Ch. 11 xls). `citation_key` / `doi` still name the **experimental paper**. `extracted_from = supplement` (or `table` if from the chapter PDF). `source_locus` names the 2010 table **and** the primary paper locus if known. `review_status = draft`. Re-extract from the PDF as soon as possible and flip the token. |
| `primary_reextract` | Same experiment that was in a 2010 compilation, now read from the primary PDF/table/equation. Replaces or supersedes the staged row (`quality_flag = superseded` on the staging row; new `record_id`; link with `related_record_id`). |
| `post2010_new` | Experimental calibration **not** in the 2010 mineral or melt tables (typically published 2011–present, or 2010 papers that missed the freeze). Wave 1 of this living DB. |

Do **not** dump Zhang Table 1 or Brady’s 484 lines as the public citation of record. Staging (`compilation_2010`) is an internal recovery step so the living table can be complete; public rows should move to `primary_reextract` or `post2010_new`.

Candidate v1.1 column: `ingest_provenance` with the same three tokens. Until then, the `notes` prefix is normative.

---

## 0.1 Recovering the 2010 v0 files (try these URLs; do not scrape a paywall)

**Melts — Zhang, Ni & Chen 2010 (RiMG 72 Ch. 8).** Landing page (live 2026-08-31):

- http://www.minsocam.org/msa/RIM/rim72.html
- alias: http://www.minsocam.org/MSA/RIM/rim72.html

Public supplement `.xls` (HTTP 200, `application/vnd.ms-excel`, confirmed 2026-08-31):

- Table 1 (~3600 D points): http://www.minsocam.org/msa/RIM/RiMG072/RiMG072_Ch08_1DiffData(melt).xls  (~1.9 MB)
- Table 2 (Arrhenius): http://www.minsocam.org/msa/RIM/RiMG072/RiMG072_Ch08_2DifDataEq(melt).xls  (~184 kB)

Author PDF of the chapter (finding aid, not a license to republish the table): http://websites.umich.edu/~youxue/publications/Zhang2010RiMG4.pdf

MSA posted those xls on a public volume page. Download for **local staging / column mapping / bibliography of primary DOIs**. Do not republish the xls wholesale. Map each 2010 row to a primary DOI, tag `provenance=compilation_2010`, then re-extract.

**Minerals — Brady & Cherniak 2010 (RiMG 72 Ch. 20).**

- Chapter PDF (Brady site, live previously): http://www.science.smith.edu/~jbrady/Papers/Diffusion_Data.pdf
- Advertised searchable DB: http://diffusion.smith.edu/  — **timed out 2026-08-31; treat as dead**.
- Wayback (try; 2010 path 404 this session): https://web.archive.org/web/*/http://diffusion.smith.edu/  and https://web.archive.org/web/*/http://www.science.smith.edu/~jbrady/diffusion
- If Wayback or the authors supply the 484-entry files, stage as `compilation_2010`. If not, rebuild the mineral v0 from the chapter’s reference list + primary PDFs (`primary_reextract`).

**Noble-gas mineral tables — Baxter 2010 Ch. 11** (same MSA page): `RiMG072/RiMG072_Ch11_Table1.xls` … `Table9.xls` under http://www.minsocam.org/msa/RIM/RiMG072/

If a file is **not** publicly posted, **stop**. Record the URL you tried. Do not use session cookies, campus proxy hacks, or paywalled GSW HTML as a scrape source.

---

## 0.2 One-row rule

One row = **one published Arrhenius (or Arrhenius–P) fit** **or** **one isothermal D** when the source does not report a fit you are ingesting.

- Do **not** explode a published fit onto a T-grid of synthetic D values.
- Do **not** fit unpublished Arrhenius parameters to tabulated points in v1 (if you ever must, `extracted_from = recalculated` and say so in `caveats`).
- Do **not** ingest MD/DFT/potential numbers. If the same paper also has experiments, ingest **only** the experimental calibration and set `mixed_md_experiment_flag = true`.

---

## 1. What to read (in this order)

1. **Abstract + last paragraph of the discussion** — find the recommended law and its validity window.
2. **Experimental methods** — apparatus, capsule, buffer / gas mix, orientation, hydrous vs dry, duration, geometry (thin film, couple, powder source, sorption, implantation).
3. **The equation / table that is the calibration** — D0, Ea, optional ΔVa, Tmin–Tmax, P, fO2, composition, direction. Prefer the fitted law over individual run D unless there is no fit.
4. **Figure of Arrhenius / profiles** — only to confirm the table; do not digitize a figure if a table/equation exists.
5. **Erratum** — search `"authors year" erratum|correction` before locking the row.

Record `extracted_from` as `table` | `figure` | `equation` | `text` | `supplement` | `recalculated`. Put the locator in `source_locus` (mandatory).

---

## 2. When to split rows

Split whenever the published calibration is a different object:

| Split on | Example |
|---|---|
| Diffusant | Yb vs Nd in the same diopside paper |
| Direction | olivine //[001] vs //[100] |
| Host composition | Fo90 vs Fo80; rhyolite 4.1 vs 6.2 wt% H2O |
| Hydrous vs dry | aH2O≈1 vs nominally dry |
| fO2 regime **if they fitted separately** | air vs QFM Arrhenius lines |
| Mechanism | Li interstitial vs Li vacancy (Pohl et al. 2024) |
| Record type | published fit **and** (optional) underlying isothermal points linked by `related_record_id` — v1 default is **fit only** |
| Interdiffusion partner | Fe–Mg vs Ni–Mg |

Do **not** split a single fO2-dependent law of the form `D = D0 (fO2)^n exp(−Ea/RT)` into one row per buffer. Store **one** fit; put *n* and the fO2 unit in `notes` / `caveats` (see §5).

Interdiffusion is **one** row: `diffusant` + `co_diffusant` + `diffusion_type = interdiffusion` (e.g. `Fe` / `Mg`).

EBD / crystal-dissolution D in melt is `diffusion_type = chemical`, `diffusion_type_qualifier = effective_binary`. Quote the authors’ wording in `notes` (“MgO EBD during olivine dissolution…”).

Multicomponent melt **matrices** (Guo & Zhang 2018/2020; Bai & Zhang 2025): v1 stores scalar EBD or published **eigenvalue** Arrhenius lines, not the (N−1)×(N−1) matrix. Point to the matrix paper in `notes`. `diffusion_type_qualifier = multicomponent_dij`.

---

## 3. Unit conversions (always; never leave implicit)

Canonical store: D and D0 in **m² s⁻¹**; T in **K**; P in **Pa**; Ea in **J mol⁻¹**; ΔVa in **m³ mol⁻¹**. Also store the printed number in `*_original_value` + `*_original_unit`.

| Printed | Canonical |
|---|---|
| D or D0 in cm²/s | × 10⁻⁴ → m²/s |
| log10 D (cm²/s) | − 4 → log10 D (m²/s) |
| ln D0 | `log10_d0_m2_s = lnD0 / ln(10)` (same unit system first) |
| Ea in kJ/mol | × 10³ → J/mol |
| Ea in kcal/mol | × 4184 → J/mol |
| Ea in eV | × 96485 → J/mol |
| E/R in K | Ea = (E/R) × R; set `arrhenius_equation_form = E_over_R` |
| ΔVa in cm³/mol | × 10⁻⁶ → m³/mol |
| 1 GPa | 1e9 Pa |
| 1 kbar / 1 kb | 1e8 Pa |
| 1 bar | 1e5 Pa |
| 1 atm / “ambient 1-atm furnace” | **101325 Pa** |
| T in °C | + 273.15 → K |

`log10_d0_m2_s = log10(d0_m2_s)`. If the paper quotes only log10 D0, fill `log10_d0_m2_s` and compute `d0_m2_s`.

Set `arrhenius_equation_form` to the **equation they fitted**, not the one you prefer:

- `D=D0*exp(-Ea/RT)`
- `D=D0*exp(-(Ea+P*dVa)/RT)`
- `log10D=log10D0-Ea/(2.303RT)`
- `lnD=lnD0-Ea/RT`
- `E_over_R`
- `other` (mandatory explanation in `notes`)

If R is unstated, store `gas_constant_used_j_mol_k = 8.314` and say so in `notes`.

**Do not invent D0 or Ea.** If only isothermal D is given, `record_type = isothermal_d`; leave all `d0_*` / `ea_*` / `activation_volume_*` empty.

For `arrhenius_fit`: fill `t_min_k`–`t_max_k` with the **experimental window of the fit**, not a geologic extrapolation. `t_k` is a reference T only if they quote one. For `isothermal_d`, `t_k = t_min_k = t_max_k`.

Zhang 2010 Table 2 stores `ln D0` (D0 in m²/s) and `E/R` in K. Convert: `log10_d0_m2_s = lnD0 / 2.302585`; `ea_j_mol = (E/R) * R`.

Brady 2010 typically stores log10 D0 (often cm²/s) and Ea. Confirm the log unit before converting.

---

## 4. Host, type, method

- `host_type`: `mineral` | `melt` (glasses are `melt`).
- `host_name`: Title case (`Olivine`, `Diopside`, `Zircon`, `Rhyolite`, `Basalt`).
- `host_ima_name`: IMA lowercase for minerals (`forsterite`, `diopside`, `zircon`).
- `host_group`: controlled token (`olivine`, `pyroxene`, `garnet`, `feldspar`, `accessory`, `phosphate`, `melt_basalt`, `melt_rhyolite`, …).
- `diffusion_type`: `self` | `tracer` | `chemical` | `interdiffusion`. If authors say “tracer” for EBD, recode to `chemical` + `effective_binary`.
- `method`: prefer the **analytical** token (`SIMS`, `RBS`, `EPMA`, `LA-ICP-MS`, `FTIR`, …); put geometry in `experiment_geometry`.
- `direct_measurement_flag = true` for profile / bulk-exchange laboratory D. v1 excludes viscosity-, conductivity-, and natural-zoning inversions.
- `anisotropy_flag = true` if the row is direction-specific; `crystallographic_direction` normalized (`[001]`, `[100]`, `//c`, `isotropic`, `melt`).

---

## 5. How to record fO2

Controlled tokens only: `NNO` | `QFM` | `IW` | `air` | `measured` | `unknown` plus extended `MH`, `WM`, `IW-C`/`CCO`, `G`, `NNO-H2O`, `QFM-H2O`.

- **Always `QFM`, never `FMQ`.**
- Offsets live in `fo2_buffer_offset`, not in the token: QFM+1 → `fo2_buffer = QFM`, `fo2_buffer_offset = +1`.
- Solid buffer in the charge → `fo2_constraint = buffered`.
- CO–CO2 / H2–CO2 furnace, even if they say “near QFM” → `fo2_buffer = QFM` (or `measured` if they report a sensor number and no named buffer), `fo2_constraint = gas_mix`.
- Air furnace → `fo2_buffer = air`, `fo2_constraint = unconstrained`.
- Graphite furnace / piston-cylinder with C → `G` or `IW-C` as appropriate; do not guess QFM.
- Not reported and not inferable → `unknown` / `unknown`.

`log10_fo2_bar` is **log10(fO2 / 1 bar)**, not log10(Pa). Conversion: `log10(fO2/bar) = log10(fO2/Pa) − 5`.

**fO2-dependent Arrhenius** `D = D0 (fO2)^n exp(−Ea/RT)`:

- One row for the published law.
- Store the printed D0 with its **stated fO2 reference** (often fO2 = 1 in the unit they used). Write the unit of fO2 (Pa vs bar) and *n* in `notes`.
- Do not silently absorb a buffer into D0. If they only publish D0 at NNO, say `D0 at NNO` in `notes` and set `fo2_buffer = NNO`.

---

## 6. `quality_flag` rules (compiler judgement)

| Token | Use when |
|---|---|
| `recommended` | Direct profile, T window ≥ ~150 K or ≥ 4 T points, fO2 and orientation stated (or melt / cubic), no unresolved method conflict. Default for community workhorse laws after you have read the PDF. |
| `use_with_caution` | Short profiles vs analytical resolution (RBS/SIMS convolution); T window < ~100 K; fO2 unbuffered in an Fe-bearing host; H2O unmeasured when D is water-sensitive; polycrystalline with possible GB tail; concentration-dependent D collapsed to one number; fO2 exponent folded into D0 without a stated reference; `compilation_2010` staging not yet re-extracted. |
| `disputed` | Later experimental work shows a different mechanism or order-of-magnitude offset **and** the community has not settled (cite the dispute in `caveats`). |
| `superseded` | A later paper from the same system is the intended replacement, **or** a `primary_reextract` replaces a `compilation_2010` staging row. Keep the old row; point `related_record_id` / `caveats` at the new `record_id`. Do not delete. |
| `insufficient_metadata` | Cannot recover T window, host, or units well enough to convert. Prefer skipping the row in v1. |

Zhang-style “do not use for modeling” (convection, β-track, order-of-magnitude estimates) → `use_with_caution` or skip.

---

## 7. What to put in `source_locus`

A locator a second compiler can find in **<10 s**. Combine with `extracted_from`.

Good: `Eq. 1; Table 2` · `Abstract (1-atm Arrhenius, D ⊥ (001))` · `Zhang 2010 Table 2 xls, row …; primary Eq. unknown` · `Pohl 2024 Eqs. 21–22 (CC-BY HTML)`.

Bad: `paper` · `see text` · `Fig. 4` alone if the figure is not the source of the numbers.

If you used an author-hosted PDF, MSA public-access PDF, or publisher abstract because the typeset PDF was paywalled, say so. Keep `review_status = draft` until the typeset PDF table/equation is checked.

---

## 8. Checklist before saving

- [ ] `notes` starts with `provenance=…` (one of the three tokens).
- [ ] `doi` is the **primary experimental** paper (not 10.2138/rmg.2010.72.8 or .20).
- [ ] `record_type` matches filled vs empty D0/Ea vs D columns.
- [ ] SI conversion done **and** originals stored.
- [ ] `t_min_k`–`t_max_k` and `p_min_pa`–`p_max_pa` are the calibration window.
- [ ] `fo2_buffer` is a controlled token; offset is numeric; log fO2 is per **bar**.
- [ ] Split test: direction / composition / H2O / species / mechanism / fit vs isothermal.
- [ ] `quality_flag`, `extracted_from`, `source_locus`, `citation_key`, `compiler`, `compilation_date` (`YYYY-MM-DD`), `review_status` (`draft` until a second pass).
- [ ] No invented D0/Ea.

Start `review_status = draft`. Promote to `checked` after a PDF pass against the original table/equation; `verified` only after a second person (or a later sitting) agrees.
