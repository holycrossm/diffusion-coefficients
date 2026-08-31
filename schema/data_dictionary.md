# Data dictionary — experimentally calibrated diffusion coefficients

**Schema version:** 1.0.0
**File:** `schema.csv` (header only; no data rows)
**Encoding:** UTF-8, comma-separated, Unix line endings, decimal point (not comma).
**Missing values:** empty cell. Do not use `NA`, `n/a`, `-`, or `9999` as sentinels.
**Booleans:** `true` | `false` (lowercase).
**Dates:** ISO 8601 `YYYY-MM-DD`.
**Identifiers:** ASCII snake_case column names; do not rename in place (add columns in later schema versions).

Canonical stored units are SI. Every quantity that a source reports in non-SI units is **also** stored as reported (`*_original_value` + `*_original_unit`) so conversions remain auditable. Petrologic conventions that are not SI (oxide wt%, log10 *f*O2 in bar) are stored in those conventional units and labelled as such.

**Row definition (normative):** one row is either (a) one experimentally constrained Arrhenius (or Arrhenius–pressure) fit, or (b) one isothermal diffusivity at stated conditions when the source does not report a fit. See `record_type`. Do not explode a published fit into synthetic isothermal rows, and do not fit unpublished Arrhenius parameters to tabulated points unless that fit is clearly labelled in `fit_notes` / `caveats` as compiler-derived.

---

## 0. Controlled vocabularies (normative, v1)

Use only the tokens below in the named columns. If a source needs a value not listed, set the column to `other` (where allowed) and put the source wording in the associated notes field. Do not invent near-synonyms (`FMQ` vs `QFM` — always `QFM`).

### `host_type`

| Token | Meaning |
|---|---|
| `mineral` | Crystalline host (including hydrous minerals, oxides, phosphates, carbonates, sulfides). |
| `melt` | Silicate liquid **or** supercooled silicate glass treated as a melt/glass in the source. |

Glasses are `host_type = melt`. Record `T` relative to the glass transition in `notes` if relevant. Non-silicate melts (carbonatite, sulfide liquid, metal) are out of v1 scope.

### `diffusion_type`

Definitions follow Brady (1975, 1995), Zhang (2010, RiMG 72), and Brady & Cherniak (2010).

| Token | Meaning |
|---|---|
| `self` | Diffusion of a major structural species in the absence of a chemical concentration gradient, typically measured with an isotopic tracer of that same element (e.g. ¹⁸O, ²⁶Mg, ³⁰Si). |
| `tracer` | Diffusion of a dilute impurity / radiogenic / exotic species that does not itself impose a chemical gradient of a major component. Includes radiotracer and many SIMS/RBS “thin-film” impurity studies. |
| `chemical` | Diffusivity describing flux down a chemical potential / concentration gradient of the component (includes effective binary diffusion, EBD). |
| `interdiffusion` | Binary (or pseudo-binary) exchange of two species (e.g. Fe–Mg, Na–K, Ar–Ab). Use `co_diffusant` for the exchanging partner. |

If a paper calls EBD “tracer diffusion,” recode to `chemical` and set `diffusion_type_qualifier = effective_binary`. Record the authors’ original wording in `notes`.

### `method`

Coarse primary tag matching community shorthand. Prefer the **analytical** technique when both a geometry and an analysis are reported; put geometry in `experiment_geometry`.

| Token | Meaning |
|---|---|
| `SIMS` | Secondary ion mass spectrometry (including ion-probe line scans and depth profiles). |
| `NanoSIMS` | NanoSIMS specifically. |
| `RBS` | Rutherford backscattering spectrometry. |
| `NRA` | Nuclear reaction analysis. |
| `ERDA` | Elastic recoil detection analysis (H, D). |
| `EPMA` | Electron probe microanalysis (WDS/EDS). |
| `LA-ICP-MS` | Laser ablation ICP-MS (line or depth). |
| `FTIR` | Infrared spectroscopy (H, OH, H2O, CO2, etc.). |
| `Raman` | Raman spectroscopy. |
| `NMR` | Nuclear magnetic resonance, including PFG-NMR. |
| `couple` | Diffusion-couple experiment in which the couple itself is the identifying method (analysis recorded separately if known). |
| `thin_film` | Thin-film or surface-source experiment (analysis recorded separately if known). |
| `sorption` | Sorption / desorption / hydration–dehydration kinetics. |
| `radiotracer` | Radiotracer + serial sectioning, residual activity, or autoradiography. |
| `autoradiography` | Autoradiography as the profile method. |
| `serial_sectioning` | Mechanical serial sectioning / grinding. |
| `crystal_dissolution` | Diffusivity recovered from crystal dissolution / growth in melt. |
| `ion_implantation` | Implanted-source experiments. |
| `other` | Anything else; mandatory detail in `analytical_technique` and `notes`. |

`analytical_technique` may repeat or refine `method` (e.g. `method = couple`, `analytical_technique = SIMS`).

### `fo2_buffer`

| Token | Meaning |
|---|---|
| `NNO` | Ni–NiO buffer. |
| `QFM` | Quartz–fayalite–magnetite (same as FMQ; **always store `QFM`**). |
| `IW` | Iron–wüstite. |
| `air` | Air / unconstrained 1-atm air furnace. |
| `measured` | *f*O2 measured (sensor, gas mix with reported log *f*O2), not a solid buffer. |
| `unknown` | Not reported and not inferable. |

**Extended tokens permitted in v1** (still controlled): `MH` (magnetite–hematite), `WM` (wüstite–magnetite), `IW-C` / `CCO` (C–CO), `G` (graphite), `NNO-H2O`, `QFM-H2O`. Offsets from a buffer belong in `fo2_buffer_offset`, not in the token (`QFM` + `+1`, not `QFM+1`).

---

## 1. Identity

### `record_id`
- **Meaning:** Stable primary key for the row. Assigned by the compiler; never reused if a row is retired (retire by `quality_flag = superseded` and a new id).
- **Type:** string.
- **Allowed:** `DDB` + 6 zero-padded digits, e.g. `DDB000001`. Do not encode science into the id.
- **Units:** none.
- **Required:** yes.
- **Example:** `DDB000001`

### `schema_version`
- **Meaning:** Schema release that the row was written against.
- **Type:** string, semantic version `MAJOR.MINOR.PATCH`.
- **Allowed:** `1.0.0` for this release.
- **Units:** none.
- **Required:** yes.
- **Example:** `1.0.0`

### `record_type`
- **Meaning:** Which of the two allowed row kinds this is.
- **Type:** controlled string.
- **Allowed:** `arrhenius_fit` | `isothermal_d`
  - `arrhenius_fit`: source reports D0 and Ea (and optionally ΔVa) fitted to experimental points. Store the fit, the T (and P) interval of the calibration, and `n_experiments` / `n_temperature_points`. Leave `d_m2_s` empty unless the source also quotes a D at a stated T that should be preserved as reported (then also fill `t_k`).
  - `isothermal_d`: source reports D at a stated T (and P, *f*O2, composition) **without** a fit you are ingesting. Fill `d_m2_s` (or `log10_d_m2_s`) and `t_k`. Leave D0/Ea empty.
- **Units:** none.
- **Required:** yes.
- **Example:** `arrhenius_fit`

### `related_record_id`
- **Meaning:** Optional link, e.g. isothermal points that underlie a published fit, or the mineral-hosted row paired with a melt row in the same paper.
- **Type:** string; semicolon-separated `record_id`s if several.
- **Allowed:** existing `record_id` values, or empty.
- **Units:** none.
- **Required:** no.
- **Example:** `DDB000014;DDB000015`

---

## 2. Diffusant and diffusion type

### `diffusant`
- **Meaning:** The species whose diffusivity is reported. Use the chemical identity, not the isotope (isotope goes in `diffusant_isotope`).
- **Type:** string.
- **Allowed:** element symbol (`Mg`, `Pb`, `O`, `H`, `Ar`), molecular species (`H2O`, `OH`, `CO2`), or exchange pair for interdiffusion written `Fe-Mg` (then also fill `co_diffusant`). Prefer IUGS/IUPAC element symbols. Do not store charge here.
- **Units:** none.
- **Required:** yes.
- **Example:** `Pb`

### `diffusant_isotope`
- **Meaning:** Mass number of the monitored isotope, if the experiment is isotopic.
- **Type:** string (not integer, because of `D`, `T`).
- **Allowed:** e.g. `18`, `26`, `30`, `D`, `T`; empty if not isotopic or not specified.
- **Units:** none.
- **Required:** no.
- **Example:** `18`

### `diffusant_valence`
- **Meaning:** Oxidation state of the diffusant when it matters (Fe, Eu, Cr, V, C, S, etc.).
- **Type:** string.
- **Allowed:** integer charge with sign, e.g. `2+`, `3+`, `mixed`, `unknown`, or empty if inapplicable.
- **Units:** none.
- **Required:** no (required when the element is redox-variable and the source specifies it).
- **Example:** `2+`

### `co_diffusant`
- **Meaning:** Partner species for `diffusion_type = interdiffusion`.
- **Type:** string, same conventions as `diffusant`.
- **Allowed:** element or species symbol; empty if not interdiffusion.
- **Units:** none.
- **Required:** yes if `diffusion_type = interdiffusion`; else empty.
- **Example:** `Mg`

### `diffusion_type`
- **Meaning:** Phenomenological class of the reported D. See vocabulary in §0.
- **Type:** controlled string.
- **Allowed:** `self` | `tracer` | `chemical` | `interdiffusion`
- **Units:** none.
- **Required:** yes.
- **Example:** `tracer`

### `diffusion_type_qualifier`
- **Meaning:** Finer classification without exploding `diffusion_type`.
- **Type:** controlled string.
- **Allowed:** `none` | `effective_binary` | `multicomponent_dij` | `isotopic` | `ionic` | `molecular` | `empty` treated as `none`.
- **Units:** none.
- **Required:** no.
- **Example:** `effective_binary`

### `reference_frame`
- **Meaning:** Reference frame of the reported D (Brady 1975, Am J Sci). Required in principle for chemical/interdiffusion; usually implicit for tracer/self.
- **Type:** controlled string.
- **Allowed:** `lattice` | `volume` | `solvent` | `barycentric` | `unspecified`
- **Units:** none.
- **Required:** no (strongly recommended for `chemical` and `interdiffusion`).
- **Example:** `lattice`

---

## 3. Host

### `host_type`
- **Meaning:** Mineral vs silicate melt/glass. See §0.
- **Type:** controlled string.
- **Allowed:** `mineral` | `melt`
- **Units:** none.
- **Required:** yes.
- **Example:** `mineral`

### `host_name`
- **Meaning:** Community name used for indexing (mineral species or melt lithology / endmember melt).
- **Type:** string.
- **Allowed:** lowercase-with-spaces avoided; use Title case mineral names (`Olivine`, `Diopside`, `Zircon`, `Sanidine`) and melt names (`Rhyolite`, `Basalt`, `Albite melt`, `Haplogranite`). One host per row.
- **Units:** none.
- **Required:** yes.
- **Example:** `Zircon`

### `host_ima_name`
- **Meaning:** IMA-CNMNC approved mineral name, if `host_type = mineral`.
- **Type:** string.
- **Allowed:** IMA name (`zircon`, `forsterite`, `diopside`) or empty for melts / unnamed synthetics.
- **Units:** none.
- **Required:** no (recommended for minerals).
- **Example:** `zircon`

### `host_formula`
- **Meaning:** Simplified structural formula of the host.
- **Type:** string.
- **Allowed:** plain text, no markup. Use standard mineral formulae or melt CIPW-style only if that is what was reported.
- **Units:** none.
- **Required:** no.
- **Example:** `ZrSiO4`

### `host_endmember`
- **Meaning:** Endmember proportion string as used by experimentalists.
- **Type:** string.
- **Allowed:** e.g. `Fo90`, `Di`, `Ab`, `Pyr70Alm20Grs10`, `An45`. Empty if not applicable.
- **Units:** none (proportions are part of the string).
- **Required:** no.
- **Example:** `Fo90`

### `host_group`
- **Meaning:** Broad mineral/melt group for filtering.
- **Type:** controlled string.
- **Allowed:** `olivine` | `pyroxene` | `garnet` | `feldspar` | `feldspathoid` | `amphibole` | `mica` | `quartz_silica` | `accessory` | `oxide` | `phosphate` | `carbonate` | `sulfide` | `melt_rhyolite` | `melt_dacite` | `melt_andesite` | `melt_basalt` | `melt_ultramafic` | `melt_alkaline` | `melt_simple` | `other`
- **Units:** none.
- **Required:** no (recommended).
- **Example:** `accessory`

### `host_origin`
- **Meaning:** Natural crystal/glass vs laboratory synthesis.
- **Type:** controlled string.
- **Allowed:** `natural` | `synthetic` | `mixed` | `unknown`
- **Units:** none.
- **Required:** no.
- **Example:** `synthetic`

### `crystallographic_direction`
- **Meaning:** Direction of the measured D relative to crystallographic axes. Empty / `isotropic` / `melt` when anisotropy is not defined.
- **Type:** string.
- **Allowed:** Miller or axis notation as reported, normalized where possible: `//c`, `//a`, `[100]`, `[001]`, `[010]`, `//n_beta`, `isotropic`, `polycrystalline`, `melt`, `glass`, `unspecified`.
- **Units:** none.
- **Required:** no (required when the source reports anisotropy).
- **Example:** `[001]`

### `anisotropy_flag`
- **Meaning:** Whether this row is a direction-specific measurement (as opposed to an isotropic/average D).
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** yes.
- **Example:** `true`

### `polycrystal_flag`
- **Meaning:** Whether the specimen was polycrystalline (grain-boundary risk).
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** no (default interpret empty as unknown, not false).
- **Example:** `false`

---

## 4. Host composition

Oxide columns are **mass percent of the host as analyzed** (anhydrous 100% or as-reported; state which in `composition_notes`). Do not recalculate Fe speciation unless the source does; put total iron in `feot_wt_pct` as FeO* when that is what was reported.

### `composition_as_reported`
- **Meaning:** Verbatim or lightly normalized composition string from the paper (table, text, or supplement). The audit trail; oxide columns may be empty if parsing is deferred.
- **Type:** string.
- **Allowed:** free text; prefer semicolon-separated `oxide=value` if normalizing.
- **Units:** as in the source (declare in `composition_basis`).
- **Required:** yes if any quantitative composition is given; otherwise empty and explain in `composition_notes`.
- **Example:** `SiO2=66.8;Al2O3=13.1;Na2O=4.5;K2O=4.2;H2O=0.1 wt%`

### `composition_basis`
- **Meaning:** Unit system of `composition_as_reported` and the oxide columns.
- **Type:** controlled string.
- **Allowed:** `wt_pct_oxide` | `mol_pct_oxide` | `cation_formula` | `endmember_mol_frac` | `unspecified`
- **Units:** n/a (this field *names* the units).
- **Required:** yes if composition is stored.
- **Example:** `wt_pct_oxide`

### `sio2_wt_pct` … `nio_wt_pct`
- **Meaning:** Major-element host composition, always converted to **weight percent oxide** for the structured columns even if the source used mol%. Keep the source numbers in `composition_as_reported`.
- **Type:** float.
- **Allowed:** ≥ 0; empty if not reported. `feot_wt_pct` is total iron as FeO*. `feo_wt_pct` / `fe2o3_wt_pct` only if the source speciates Fe.
- **Units:** wt% (g/100 g).
- **Required:** no.
- **Example:** `sio2_wt_pct = 40.12` (forsteritic olivine)

Columns: `sio2_wt_pct`, `tio2_wt_pct`, `al2o3_wt_pct`, `cr2o3_wt_pct`, `feot_wt_pct`, `feo_wt_pct`, `fe2o3_wt_pct`, `mno_wt_pct`, `mgo_wt_pct`, `cao_wt_pct`, `na2o_wt_pct`, `k2o_wt_pct`, `p2o5_wt_pct`, `nio_wt_pct`.

### `other_oxides`
- **Meaning:** Additional oxides or elements not given dedicated columns.
- **Type:** string, `name=value` pairs separated by semicolons; values in wt% unless stated.
- **Allowed:** e.g. `ZrO2=0.15;V2O5=0.02;F=0.08;Cl=0.01;SO3=0.03`
- **Units:** wt% unless tagged.
- **Required:** no.
- **Example:** `ZrO2=67.2`

### `mg_number`
- **Meaning:** 100 × Mg/(Mg+Fe) on a molar basis, using the iron basis the source used (state Fe2+ vs Fetot in `composition_notes`).
- **Type:** float.
- **Allowed:** 0–100.
- **Units:** dimensionless (percent).
- **Required:** no.
- **Example:** `90.2`

### `nbo_t`
- **Meaning:** Non-bridging oxygen per tetrahedron, for melts. Compiler-calculated values must be flagged in `composition_notes`.
- **Type:** float.
- **Allowed:** ≥ 0, or empty.
- **Units:** dimensionless.
- **Required:** no.
- **Example:** `0.15`

### `composition_notes`
- **Meaning:** Fe basis, volatile-free vs hydrous totals, microprobe vs bulk, zoning, starting-material vs post-run, etc.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** no.
- **Example:** `FeOt as reported; anhydrous normalized to 100%; EPMA of starting glass.`

---

## 5. Water / aH2O

Water is stored separately from major oxides even though H2O is part of composition, because of its first-order effect on D (Zhang et al. 2010; Behrens 2010).

### `hydrous_flag`
- **Meaning:** Whether the experiment is intended as hydrous (added H2O, hydrothermal, or measured H2O above nominally dry).
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** yes.
- **Example:** `false`

### `h2o_wt_pct`
- **Meaning:** Total water content of the host during the diffusion anneal (preferred: measured post-run).
- **Type:** float.
- **Allowed:** ≥ 0; empty if nominally dry and unmeasured.
- **Units:** wt% H2O.
- **Required:** no (recommended whenever hydrous or when “nominally dry” was actually measured).
- **Example:** `5.2`

### `h2o_wt_pct_min` / `h2o_wt_pct_max`
- **Meaning:** Range when H2O varies along a profile or across the experimental series represented by this row. For a single-value row, leave empty and use `h2o_wt_pct`.
- **Type:** float.
- **Allowed:** ≥ 0; max ≥ min.
- **Units:** wt% H2O.
- **Required:** no.
- **Example:** `0.1` / `4.8`

### `a_h2o`
- **Meaning:** Water activity imposed or calculated for the experiment.
- **Type:** float.
- **Allowed:** 0–1 in the standard state declared in `water_notes`.
- **Units:** dimensionless activity.
- **Required:** no.
- **Example:** `1.0`

### `water_notes`
- **Meaning:** How H2O was loaded and measured (FTIR 3570 cm−1, Karl Fischer, manometry), speciation (OH vs H2O mol), standard state of aH2O, whether “nominally dry” means unmeasured.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** no.
- **Example:** `aH2O=1, H2O-saturated; total H2O by FTIR; species not resolved.`

---

## 6. Intensive conditions (T, P, fO2)

Canonical T is kelvin, canonical P is pascal. log10 *f*O2 follows the petrologic convention **log10(*f*O2 / 1 bar)** (1 bar = 10⁵ Pa). Always store the source’s numbers in the `*_original_*` pair.

For `arrhenius_fit` rows, `t_k` / `p_pa` are the **reference or midpoint** conditions of the fit if the source quotes one; the calibration window is `t_min_k`–`t_max_k` and `p_min_pa`–`p_max_pa`. For `isothermal_d` rows, `t_k` and `p_pa` are the actual run conditions.

### `t_k`
- **Meaning:** Temperature of the isothermal D, or reference T of a fit.
- **Type:** float.
- **Allowed:** > 0.
- **Units:** K.
- **Required:** yes for `isothermal_d`; recommended for `arrhenius_fit` if a reference T is given.
- **Example:** `1473.15`

### `t_min_k` / `t_max_k`
- **Meaning:** Inclusive experimental temperature window of the calibration (the range over which the Arrhenius fit is valid, **not** a geologic extrapolation).
- **Type:** float.
- **Allowed:** `t_max_k` ≥ `t_min_k` > 0. For a single-T row, set both equal to `t_k`.
- **Units:** K.
- **Required:** yes.
- **Example:** `1073.15` / `1673.15`

### `t_original_value` / `t_original_unit`
- **Meaning:** Temperature as printed in the source.
- **Type:** float + string.
- **Allowed units:** `C` | `K` | `F` (F rare; still preserve).
- **Required:** no (recommended).
- **Example:** `1200` / `C`

### `p_pa`
- **Meaning:** Pressure of the isothermal D, or reference / constant P of a fit. 1 atm = 101325 Pa.
- **Type:** float.
- **Allowed:** ≥ 0.
- **Units:** Pa.
- **Required:** yes. If the source says “1 atm” / “ambient” and gives no number, store `101325`.
- **Example:** `1000000000` (1 GPa)

### `p_min_pa` / `p_max_pa`
- **Meaning:** Pressure window of the calibration. Equal to `p_pa` when P is fixed.
- **Type:** float.
- **Allowed:** max ≥ min ≥ 0.
- **Units:** Pa.
- **Required:** yes.
- **Example:** `101325` / `101325`

### `p_original_value` / `p_original_unit`
- **Meaning:** Pressure as printed in the source.
- **Type:** float + string.
- **Allowed units:** `Pa` | `kPa` | `MPa` | `GPa` | `bar` | `kbar` | `kb` | `atm`.
- **Required:** no (recommended).
- **Example:** `1` / `GPa`

### `fo2_buffer`
- **Meaning:** Solid buffer or atmosphere class. See §0.
- **Type:** controlled string.
- **Allowed:** `NNO` | `QFM` | `IW` | `air` | `measured` | `unknown` plus the extended tokens in §0.
- **Units:** none.
- **Required:** yes.
- **Example:** `QFM`

### `fo2_buffer_offset`
- **Meaning:** log10 units relative to the named buffer, as in QFM+1 → buffer `QFM`, offset `+1`.
- **Type:** float (signed).
- **Allowed:** any real; empty if buffer is `air`, `measured`, or `unknown` without an offset.
- **Units:** log10 *f*O2 units (dimensionless).
- **Required:** no.
- **Example:** `-1`

### `log10_fo2_bar`
- **Meaning:** Absolute oxygen fugacity on the conventional scale log10(*f*O2 / 1 bar) at the row’s T (and P, if the source reduces it that way).
- **Type:** float.
- **Allowed:** typically −30 to 0 for magmatic T; not range-checked.
- **Units:** log10(bar). **Not** log10(Pa).
- **Required:** no (required if `fo2_buffer = measured` and a number is given).
- **Example:** `-11.2`

### `fo2_constraint`
- **Meaning:** How *f*O2 was imposed.
- **Type:** controlled string.
- **Allowed:** `buffered` | `gas_mix` | `measured` | `estimated` | `unconstrained` | `unknown`
- **Units:** none.
- **Required:** yes.
- **Example:** `buffered`

### `apparatus`
- **Meaning:** Experimental device, which often implies P capability and *f*O2 control.
- **Type:** controlled string.
- **Allowed:** `one_atm_furnace` | `gas_mixing_furnace` | `cold_seal` | `internally_heated_pressure_vessel` | `piston_cylinder` | `multi_anvil` | `diamond_anvil` | `hydrothermal` | `other` | `unspecified`
- **Units:** none.
- **Required:** no (recommended).
- **Example:** `piston_cylinder`

### `duration_s`
- **Meaning:** Anneal duration (isothermal rows, or typical duration of a fit series if a single value is meaningful).
- **Type:** float.
- **Allowed:** > 0.
- **Units:** s.
- **Required:** no.
- **Example:** `86400`

---

## 7. Diffusivity and Arrhenius parameters

Canonical equation (Zhang 2010; Ni et al. 2015):

```
D = D0 * exp( -(Ea + P * ΔVa) / (R * T) )
```

with D in m² s⁻¹, T in K, P in Pa, Ea in J mol⁻¹, ΔVa in m³ mol⁻¹, R in J mol⁻¹ K⁻¹.

If the source omits ΔVa, treat ΔVa = 0 and do not invent a pressure term. If the source reports log10 D0 (Brady & Cherniak 2010 style) or ln D0 (Zhang et al. 2010 style), store both the canonical `d0_m2_s` and `log10_d0_m2_s` (log10, not ln). Conversion: `log10_d0_m2_s = log10(d0_m2_s)`; `ln D0 = ln(10) * log10 D0`.

**Common conversion (must be applied, never left implicit):**
- D (m² s⁻¹) = D (cm² s⁻¹) × 10⁻⁴
- log10 D (m² s⁻¹) = log10 D (cm² s⁻¹) − 4
- Ea (J mol⁻¹) = Ea (kJ mol⁻¹) × 10³ = Ea (kcal mol⁻¹) × 4184
- ΔVa (m³ mol⁻¹) = ΔVa (cm³ mol⁻¹) × 10⁻⁶
- 1 GPa = 10⁹ Pa; 1 kbar = 10⁸ Pa; 1 atm = 101325 Pa

### `d0_m2_s`
- **Meaning:** Pre-exponential factor D0 in SI.
- **Type:** float (scientific notation allowed).
- **Allowed:** > 0.
- **Units:** m² s⁻¹.
- **Required:** yes if `record_type = arrhenius_fit` (unless only log10 D0 is given, in which case fill `log10_d0_m2_s` and compute this).
- **Example:** `9.96e-6`

### `log10_d0_m2_s`
- **Meaning:** log10(D0 / m² s⁻¹). Stored explicitly to avoid round-trip error against papers that quote log D0.
- **Type:** float.
- **Allowed:** any real.
- **Units:** log10(m² s⁻¹).
- **Required:** recommended for `arrhenius_fit`.
- **Example:** `-5.002`

### `d0_unc_log10`
- **Meaning:** Uncertainty on `log10_d0_m2_s` (not on D0 linearly).
- **Type:** float.
- **Allowed:** ≥ 0.
- **Units:** log10(m² s⁻¹).
- **Required:** no.
- **Example:** `0.4`

### `d0_unc_type`
- **Meaning:** Meaning of the D0 uncertainty.
- **Type:** controlled string.
- **Allowed:** `1sigma` | `2sigma` | `se` | `95ci` | `unknown` | empty
- **Units:** none.
- **Required:** no.
- **Example:** `1sigma`

### `d0_original_value` / `d0_original_unit`
- **Meaning:** D0 as printed.
- **Type:** float + string.
- **Allowed units:** `m2/s` | `cm2/s` | `log10_m2/s` | `log10_cm2/s` | `ln_m2/s` | `ln_cm2/s`
- **Required:** no (recommended).
- **Example:** `-9.0` / `log10_cm2/s`

### `ea_j_mol`
- **Meaning:** Activation energy Ea (sometimes called activation enthalpy at the experimental P if the source folds PΔV into E). If the source reports a P-dependent enthalpy H(P) = Ea + PΔVa, store the **zero-P or stated-P** Ea they quote and put ΔVa in the activation-volume columns; explain in `notes` if ambiguous.
- **Type:** float.
- **Allowed:** > 0 for thermally activated diffusion (leave empty for isothermal rows).
- **Units:** J mol⁻¹.
- **Required:** yes if `record_type = arrhenius_fit`.
- **Example:** `404000`

### `ea_unc_j_mol`
- **Meaning:** Uncertainty on Ea, converted to J mol⁻¹.
- **Type:** float.
- **Allowed:** ≥ 0.
- **Units:** J mol⁻¹.
- **Required:** no.
- **Example:** `19000`

### `ea_unc_type`
- **Meaning:** Meaning of the Ea uncertainty.
- **Type:** controlled string.
- **Allowed:** `1sigma` | `2sigma` | `se` | `95ci` | `unknown` | empty
- **Units:** none.
- **Required:** no.
- **Example:** `1sigma`

### `ea_original_value` / `ea_original_unit`
- **Meaning:** Ea as printed.
- **Type:** float + string.
- **Allowed units:** `J/mol` | `kJ/mol` | `cal/mol` | `kcal/mol` | `eV` | `K` (for E/R).
- **Required:** no (recommended).
- **Example:** `404` / `kJ/mol`

### `activation_volume_m3_mol`
- **Meaning:** Activation volume ΔVa in the term PΔVa. Positive ΔVa means D decreases with P. May be negative (observed in some melt species; Shimizu & Kushiro 1984).
- **Type:** float (signed).
- **Allowed:** any real; empty if not constrained.
- **Units:** m³ mol⁻¹.
- **Required:** no (required when the source reports a P-dependent fit).
- **Example:** `5.2e-6`  (5.2 cm³ mol⁻¹)

### `activation_volume_unc_m3_mol`
- **Meaning:** Uncertainty on ΔVa.
- **Type:** float.
- **Allowed:** ≥ 0.
- **Units:** m³ mol⁻¹.
- **Required:** no.
- **Example:** `1.0e-6`

### `activation_volume_original_value` / `activation_volume_original_unit`
- **Meaning:** ΔVa as printed.
- **Type:** float + string.
- **Allowed units:** `m3/mol` | `cm3/mol` | `A3` (rare).
- **Required:** no.
- **Example:** `5.2` / `cm3/mol`

### `arrhenius_equation_form`
- **Meaning:** Which equation the source fitted, so D0/Ea are not misread.
- **Type:** controlled string.
- **Allowed:**
  - `D=D0*exp(-Ea/RT)`
  - `D=D0*exp(-(Ea+P*dVa)/RT)`
  - `log10D=log10D0-Ea/(2.303RT)`
  - `lnD=lnD0-Ea/RT`
  - `E_over_R` (source quotes Ea/R in K)
  - `other`
- **Units:** none (the token *is* the equation).
- **Required:** yes if `record_type = arrhenius_fit`.
- **Example:** `D=D0*exp(-Ea/RT)`

### `gas_constant_used_j_mol_k`
- **Meaning:** R used by the source when reconstructing D from their Ea and D0. If unstated, store `8.314` and say so in `notes`.
- **Type:** float.
- **Allowed:** typically 8.314, 8.31446, 1.987 (if they used cal; convert Ea instead of storing R in cal).
- **Units:** J mol⁻¹ K⁻¹.
- **Required:** no.
- **Example:** `8.314`

### `d_m2_s`
- **Meaning:** Diffusivity at the row’s `t_k` (and P, *f*O2, composition).
- **Type:** float (scientific notation allowed).
- **Allowed:** > 0.
- **Units:** m² s⁻¹.
- **Required:** yes if `record_type = isothermal_d`.
- **Example:** `2.5e-19`

### `log10_d_m2_s`
- **Meaning:** log10(D / m² s⁻¹) at the row conditions.
- **Type:** float.
- **Allowed:** any real.
- **Units:** log10(m² s⁻¹).
- **Required:** recommended for `isothermal_d`.
- **Example:** `-18.60`

### `d_unc_log10`
- **Meaning:** Uncertainty on `log10_d_m2_s`.
- **Type:** float.
- **Allowed:** ≥ 0.
- **Units:** log10(m² s⁻¹).
- **Required:** no.
- **Example:** `0.15`

### `d_unc_type`
- **Meaning:** Meaning of the D uncertainty.
- **Type:** controlled string.
- **Allowed:** `1sigma` | `2sigma` | `se` | `95ci` | `unknown` | empty
- **Units:** none.
- **Required:** no.
- **Example:** `1sigma`

### `d_original_value` / `d_original_unit`
- **Meaning:** D as printed.
- **Type:** float + string.
- **Allowed units:** `m2/s` | `cm2/s` | `log10_m2/s` | `log10_cm2/s` | `ln_m2/s` | `ln_cm2/s`
- **Required:** no (recommended).
- **Example:** `-14.6` / `log10_cm2/s`

### `n_experiments`
- **Meaning:** Number of experimental charges / profiles that constrain this row.
- **Type:** integer.
- **Allowed:** ≥ 1.
- **Units:** count.
- **Required:** no (strongly recommended).
- **Example:** `12`

### `n_temperature_points`
- **Meaning:** Number of distinct temperatures in an Arrhenius fit. Equals 1 for `isothermal_d`.
- **Type:** integer.
- **Allowed:** ≥ 1.
- **Units:** count.
- **Required:** no (strongly recommended for fits).
- **Example:** `6`

### `fit_r_squared`
- **Meaning:** R² of the published Arrhenius fit, if given. Not a substitute for reading the paper.
- **Type:** float.
- **Allowed:** 0–1.
- **Units:** dimensionless.
- **Required:** no.
- **Example:** `0.98`

---

## 8. Method

### `method`
- **Meaning:** Coarse primary method tag. See §0.
- **Type:** controlled string.
- **Allowed:** `SIMS` | `NanoSIMS` | `RBS` | `NRA` | `ERDA` | `EPMA` | `LA-ICP-MS` | `FTIR` | `Raman` | `NMR` | `couple` | `thin_film` | `sorption` | `radiotracer` | `autoradiography` | `serial_sectioning` | `crystal_dissolution` | `ion_implantation` | `other`
- **Units:** none.
- **Required:** yes.
- **Example:** `RBS`

### `experiment_geometry`
- **Meaning:** How the diffusion couple / source was arranged.
- **Type:** controlled string.
- **Allowed:** `thin_film` | `diffusion_couple` | `powder_source` | `ion_implantation` | `sorption` | `desorption` | `bulk_isotopic_exchange` | `crystal_dissolution` | `in_situ` | `other` | `unspecified`
- **Units:** none.
- **Required:** no (recommended).
- **Example:** `thin_film`

### `analytical_technique`
- **Meaning:** Instrument used to measure the profile or bulk exchange, refining `method`.
- **Type:** string (prefer the `method` tokens; may be semicolon-separated if two techniques were combined).
- **Allowed:** free, but prefer controlled `method` tokens.
- **Units:** none.
- **Required:** no.
- **Example:** `SIMS depth profile`

### `direct_measurement_flag`
- **Meaning:** `true` if D comes from a measured concentration (or isotopic) profile or a bulk-exchange experiment inverted with a well-posed diffusion solution. `false` if D is inverted from viscosity, electrical conductivity, geospeedometry of natural samples, or analogous indirect observables. v1 **includes only experimental laboratory calibrations**; set `false` only for laboratory indirect experiments that you have explicitly decided to keep, and explain in `caveats`. Natural geospeedometry is out of scope.
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** yes.
- **Example:** `true`

---

## 9. Quality, scope, and compiler metadata

### `grain_boundary_contribution`
- **Meaning:** Whether grain-boundary diffusion likely contaminates the reported lattice/melt D.
- **Type:** controlled string.
- **Allowed:** `none` | `possible` | `likely` | `corrected` | `unknown`
- **Units:** none.
- **Required:** yes.
- **Example:** `possible`

### `concentration_dependent_flag`
- **Meaning:** Whether D (or the reported EBD) depends on concentration of the diffusant or on host composition beyond the single composition stored on this row.
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** yes.
- **Example:** `false`

### `mixed_md_experiment_flag`
- **Meaning:** `true` if the **source paper** reports molecular-dynamics, DFT, or other theoretical D **in addition to** the experimental calibration stored in this row. The theoretical numbers are **not** ingested. `false` if the paper is experimental-only. This is the required mixed-method flag.
- **Type:** boolean.
- **Allowed:** `true` | `false`
- **Units:** none.
- **Required:** yes.
- **Example:** `false`

### `quality_flag`
- **Meaning:** Compiler judgement for downstream users, not a statement about the authors.
- **Type:** controlled string.
- **Allowed:** `recommended` | `use_with_caution` | `disputed` | `superseded` | `insufficient_metadata`
- **Units:** none.
- **Required:** yes.
- **Example:** `recommended`

### `t_calibration_notes`
- **Meaning:** Free-text restatement of the T (and P) window and any extrapolation warning. Complements `t_min_k` / `t_max_k`.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** no (recommended for fits).
- **Example:** `Fit 800–1400 C at 1 atm; do not extrapolate below 800 C (extrinsic regime may change).`

### `caveats`
- **Meaning:** Scientific caveats: surface-layer effects, convolution of SIMS/RBS resolution, possible grain-boundary tail, fO2 unbuffered, H2O unmeasured, non-Arrhenian hint, etc.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** no (recommended).
- **Example:** `Short (~50 nm) profiles; RBS depth resolution comparable to length scale.`

### `notes`
- **Meaning:** Any other compiler note, including authors’ original diffusion-type wording and equation number.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** no.
- **Example:** `Authors call this 'tracer diffusion' of Fe; recoded as chemical/EBD.`

### `extracted_from`
- **Meaning:** Where in the source the numbers were taken.
- **Type:** controlled string plus locator in `source_locus`.
- **Allowed:** `table` | `figure` | `equation` | `text` | `supplement` | `recalculated`
- **Units:** none.
- **Required:** yes.
- **Example:** `equation`

### `compiler`
- **Meaning:** Person who extracted the row.
- **Type:** string (name or ORCID).
- **Allowed:** free text.
- **Units:** none.
- **Required:** yes when data exist; for the empty schema, column is present but unused.
- **Example:** `Holycross, M.`

### `compilation_date`
- **Meaning:** Date the row was extracted or last checked against the PDF.
- **Type:** date.
- **Allowed:** `YYYY-MM-DD`.
- **Units:** none.
- **Required:** yes when data exist.
- **Example:** `2026-08-31`

### `review_status`
- **Meaning:** Curation workflow.
- **Type:** controlled string.
- **Allowed:** `draft` | `checked` | `verified` | `rejected`
- **Units:** none.
- **Required:** yes when data exist.
- **Example:** `draft`

---

## 10. Citation (citable primary source)

Cite the **experimental paper that produced the D**, not a later review, unless you are documenting a compiler recalculation (then cite both in `notes` and put the experimental DOI here). DOI is required when one exists.

### `citation_key`
- **Meaning:** Short human key, AuthorYear, disambiguated (Cherniak2001, Cherniak2001b).
- **Type:** string.
- **Allowed:** ASCII, no spaces.
- **Units:** none.
- **Required:** yes.
- **Example:** `Cherniak2001`

### `authors`
- **Meaning:** Author list as `Family, Given; Family, Given`.
- **Type:** string.
- **Allowed:** free text.
- **Units:** none.
- **Required:** yes.
- **Example:** `Cherniak, D.J.; Watson, E.B.`

### `year`
- **Meaning:** Publication year.
- **Type:** integer.
- **Allowed:** 1900–2100.
- **Units:** none.
- **Required:** yes.
- **Example:** `2001`

### `title`
- **Meaning:** Paper title.
- **Type:** string.
- **Allowed:** free text, sentence case as in the source.
- **Units:** none.
- **Required:** yes.
- **Example:** `Pb diffusion in zircon`

### `journal`
- **Meaning:** Journal, book series, or thesis institution.
- **Type:** string.
- **Allowed:** unabbreviated preferred (`Geochimica et Cosmochimica Acta`, `Reviews in Mineralogy and Geochemistry`).
- **Units:** none.
- **Required:** yes.
- **Example:** `Chemical Geology`

### `volume`
- **Meaning:** Volume (and issue if needed, as `184(3)`).
- **Type:** string (not integer — issues and supplements).
- **Allowed:** free.
- **Units:** none.
- **Required:** no.
- **Example:** `172`

### `pages`
- **Meaning:** Page range or article number.
- **Type:** string.
- **Allowed:** `start-end` or e-locator.
- **Units:** none.
- **Required:** no.
- **Example:** `105-117`

### `doi`
- **Meaning:** Digital Object Identifier of the cited source, without `https://doi.org/` prefix.
- **Type:** string.
- **Allowed:** `10.xxxx/...`. If no DOI exists (old thesis, abstract), leave empty and state so in `notes`.
- **Units:** none.
- **Required:** yes if a DOI exists.
- **Example:** `10.1016/S0009-2541(00)00233-3`

### `source_locus`
- **Meaning:** Precise locator used with `extracted_from`.
- **Type:** string.
- **Allowed:** e.g. `Table 3`, `Fig. 4`, `Eq. 2`, `Supplementary Table 1`, `p. 112`.
- **Units:** none.
- **Required:** yes.
- **Example:** `Eq. 1; Table 2`

---

## Conditional requirements (summary)

| `record_type` | Must fill | Must be empty |
|---|---|---|
| `arrhenius_fit` | `d0_m2_s` or `log10_d0_m2_s`; `ea_j_mol`; `arrhenius_equation_form`; `t_min_k`; `t_max_k` | — |
| `isothermal_d` | `d_m2_s` or `log10_d_m2_s`; `t_k`; `t_min_k = t_max_k = t_k` | `d0_*`, `ea_*`, `activation_volume_*` unless the source also quotes them for that single T (do not invent) |

Every row: `record_id`, `schema_version`, `record_type`, `diffusant`, `diffusion_type`, `host_type`, `host_name`, `anisotropy_flag`, `hydrous_flag`, `p_pa`, `p_min_pa`, `p_max_pa`, `fo2_buffer`, `fo2_constraint`, `method`, `direct_measurement_flag`, `grain_boundary_contribution`, `concentration_dependent_flag`, `mixed_md_experiment_flag`, `quality_flag`, `extracted_from`, `citation_key`, `authors`, `year`, `title`, `journal`, `doi` (if extant), `source_locus`.

---

## References for definitions (not data sources)

- Brady, J.B. (1975) Reference frames and diffusion coefficients. *American Journal of Science* 275, 954–983. doi:10.2475/ajs.275.8.954
- Brady, J.B. & Cherniak, D.J. (2010) Diffusion in minerals: an overview of published experimental diffusion data. *RiMG* 72, 899–920. doi:10.2138/rmg.2010.72.20
- Cherniak, D.J., Hervig, R., Koepke, J., Zhang, Y. & Zhao, D. (2010) Analytical methods in diffusion studies. *RiMG* 72, 107–170. doi:10.2138/rmg.2010.72.4
- Zhang, Y. (2010) Diffusion in minerals and melts: theoretical background. *RiMG* 72, 5–59. doi:10.2138/rmg.2010.72.2
- Zhang, Y., Ni, H. & Chen, Y. (2010) Diffusion data in silicate melts. *RiMG* 72, 311–408. doi:10.2138/rmg.2010.72.8
- Ni, H., Hui, H. & Steinle-Neumann, G. (2015) Transport properties of silicate melts. *Reviews of Geophysics* 53, 715–744. doi:10.1002/2015RG000485
