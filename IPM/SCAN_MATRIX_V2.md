# CSNS RCS IPM — revised scan matrix (v2), derived from the literature review

**Status: complete.** 1014 new 100k-particle CSVs in `output/v2/` (finished 2026-09-12 05:48 UTC). XMLs from `python3 scripts/write_v2_configs.py --write` (reuse skipped; extraction ions abort if generation and first-bunch centres differ by more than 1 ns). Re-run with `JOBS=4 ./scripts/run_v2.sh` (SKIP-if-exists). No v1 CSV was overwritten.

**Source.** Every change below is traced to a section of [`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) (the comparison matrix in its Section 5 in particular). The v1 matrices are described in `configs/csns_rcs_ipm/emode/README.md` and `configs/csns_rcs_ipm/imode/README.md`.

---

## 1. What the review changes

| Review finding | Consequence for the matrix | Block |
|---|---|---|
| §3.5 Extraction ions are generated 125 ns before the first field-carrying bunch; ext. H₂⁺ is a lower bound (+33 % vs ≈ +100 % aligned) | **Re-run all extraction ion points with aligned timing** (tracking train `LongitudinalOffset` = −4σₜ = −80 ns). As-run extraction ion CSVs are kept but superseded. | I1 |
| §3.4 B changes ion widths by < 0.5 % up to 200 G; 0.1 T moves H₂⁺ by ≈ 10 % | **Drop 200 G** from every ion block; keep 0 G and the 0.1 T design field | I1–I3 |
| §3.6 Ion Δx = 5, 10 mm leaves width and centroid unchanged at 100 kW; only the 500 kW aperture pull is new | **Drop Δx = +5 mm**; keep (10, 0), (0, ±5) | I1 |
| §3.6 Ion size law σ₀^−2 verified on 18 sizes | Size scan **reduced to 6 sizes** (3, 5, 7, 10, 15, 20 mm) | I1 |
| §3.7 Correction recipe needs h(σ₀, N, V, species) — v1 has only 5 powers ≥ 100 kW | **Look-up block**: 10 powers from 20 to 500 kW × 5 sizes × 3 species, injection and aligned extraction, 0 G | I2 |
| §3.1 CSNS ions are in the mixed regime (bunch ≈ τ₀); heavy ions at extraction see two bunches | **Single-bunch vs 3-bunch train** at 100 kW to isolate the multi-bunch term (Shiltsev 1 + 0.8 t_b/τ₀) | I3 |
| §2.3 Δ(B) zeros are spaced by ΔB = π mₑ/(e·ToF) ∝ √V to ≤ 5 % | **Replace uniform 5 G grids by phase-aware grids**: 12 values at k·ΔB (zeros) and (k+½)·ΔB (extrema), k = 1…6, plus 0 and 1000 G — 14 points instead of 61 | E3 |
| §2.1 / §2.6 No published low-β benchmark; the N/β column recovers only part of the injection gap | **Ramp / β scan**: 80, 200, 400, 800, 1200, 1600 MeV at fixed σ = 10 mm and fixed σₜ ∈ {120, 20 ns}, so β is the only variable | E1 |
| §2.4 σ = 3 mm extraction is +1.5 % at 300 G; PRAB fit says 320 G; 0.1 T already on the diagonal | **No extra small-beam B fill-in** — v1 Block B already has 3–20 mm at 0/100/200/300/1000 G | — |
| §2.6 CSNS commissioning runs at ≈ 80 kW (IBIC'24); v1 starts at 100 kW | **Low-power points** 20, 50, 80 kW for the three reference beams at 0/100/200/300/1000 G | E4 |
| Block C at 5 kV: ΔB = 23 G but the grid was 25 G | 5 kV dropped from the voltage axis (unresolvable, and outside the CSNS operating range) | E3 |
| §2.1 The 1 % threshold definition ("last excursion") is stricter than the PRAB τ | Analysis change, no runs: report the **envelope** of Δ(B) (peak amplitude per lobe) alongside the strict threshold | — |
| §2.6 / §6 Field non-uniformity, MCP, secondary electrons | **Blocked**: needs the CST/measured cage field map from the hardware group; not counted below | — |

## 2. Axes: v1 versus v2

| Axis | v1 | v2 | Reason |
|---|---|---|---|
| e-mode B grid | 0–300 G / 5 G (61), + 1000 G | 14 phase-aware values per voltage (E3); 0/100/200/300/500/1000 G (E1) | §2.3 zeros predicted; envelope decays by 300 G |
| e-mode voltage | 5–30 kV / 5 kV on inj. 10 mm (+ 1 kV fine C) | 10, 15, 20, 30 kV on **ext. 10 mm and inj. 25 mm** (25 kV = Block A) | Block C covered one beam only |
| e-mode power | 100–500 kW / 100 kW | + 20, 50, 80 kW on reference beams | commissioning powers |
| e-mode beam energy | 80 MeV and 1.6 GeV only | 6 energies along the ramp, σₜ fixed | low-β benchmark |
| e-mode size | 3–20 mm / 1 mm at 0–300, 1000 G | none — v1 Block B is complete | 0.1 T already brings 3 mm onto the diagonal |
| e-mode offsets | Δy ±10 mm / 1 mm; Δx 5, 10 mm | none | §2.5: < 0.65 % at 300 G, translation invariant |
| ion B | 0, 200, 1000 G | 0, 1000 G | §3.4 |
| ion extraction timing | generation 80 ns / first bunch 204.6 ns | aligned (both 80 ns) | §3.5 |
| ion size | 3–20 mm / 1 mm | 3, 5, 7, 10, 15, 20 mm (extraction only; injection complete) | σ₀^−2 law verified |
| ion power | 100–500 kW | 20–500 kW, 10 values (I2, 0 G) | correction look-up |
| ion voltage | 5–30 kV inj. 10 mm | 5–30 kV **ext.** 10 mm, aligned, 0 G | injection complete; extraction superseded |
| ion offsets | (5,0), (10,0), (0,±5) | (10,0), (0,±5), extraction aligned only | §3.6 |
| ion bunch train | 3-bunch circular | + single bunch (I3) | mixed-regime term |

## 3. Revised blocks

Common settings unchanged from v1: 100 000 secondaries per run, round beams σ_y = σ_x, Voitkiv H₂ DDCS (electrons) / ZeroMomentum ions of 2, 18, 28 u, Boris tracker, N_b ∝ P (7.8 × 10¹² at 100 kW), uniform E_y = V/231 mm, RNG 1234. SC-off runs do not depend on N and are written once per (beam, σ, V, B); ion SC-off is mass-independent and written for H₂⁺ only.

### Electron mode

| Block | Beam(s) | σ | B [G] | V [kV] / P [kW] | SC-on / SC-off |
|---|---|---|---|---|---|
| **E1** ramp | 80, 200, 400, 800, 1200, 1600 MeV (β = 0.39, 0.57, 0.71, 0.84, 0.90, 0.93); σₜ = 120 ns and 20 ns at every energy | 10 mm | 0, 100, 200, 300, 500, 1000 | 25 / 100, 500 | 144 / 72 |
| **E3** phase-aware voltage scan | ext. 1.6 GeV; inj. 80 MeV | 10 mm; 25 mm | 14 per voltage (table below) | 10, 15, 20, 30 / 100, 500 | 224 / 112 |
| **E4** low power | inj. 25 mm; ext. 10 mm; inj. 10 mm | ref. | 0, 100, 200, 300, 1000 | 25 / 20, 50, 80 (SC-off from Block A) | 45 / 0 |

Phase-aware B grids (zeros k·ΔB and extrema (k+½)·ΔB, rounded to 5 G; ΔB = π mₑ/(e·ToF), ToF = √(2·115.5 mm·mₑ/(e·V/231 mm))):

| V | ΔB | Grid [G] |
|---:|---:|---|
| 10 kV | 32.4 G | 0, 15, 30, 50, 65, 80, 95, 115, 130, 145, 160, 180, 195, 1000 |
| 15 kV | 39.7 G | 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 1000 |
| 20 kV | 45.9 G | 0, 25, 45, 70, 90, 115, 140, 160, 185, 205, 230, 250, 275, 1000 |
| 30 kV | 56.2 G | 0, 30, 55, 85, 110, 140, 170, 195, 225, 255, 280, 310, 335, 1000 |

Revolution period and bunch spacing for E1 follow from β and the 227.92 m circumference (T_rev = C/βc; spacing = T_rev/2, h = 2). The two σₜ values are deliberately *not* the real ramp values: E1 isolates β at fixed bunch length. A ramp-realistic variant needs the measured bunch-length table (WCM) and is listed under open inputs.

### Ion mode

All ion blocks: three species (H₂⁺, H₂O⁺, N₂⁺), 25 kV unless scanned.

| Block | Beam(s) | σ | B [G] | Axis scanned | P [kW] | SC-on / SC-off |
|---|---|---|---|---|---|---|
| **I1** aligned extraction | ext. 1.6 GeV | 3, 5, 7, 10, 15, 20 mm | 0, 1000 | size | 100–500 | 180 / 12 |
| | ext. | 10 mm | 0 | V = 5, 10, 15, 20, 30 kV | 100, 500 | 30 / 5 |
| | ext. | 10 mm | 0, 1000 | (Δx, Δy) = (10, 0), (0, +5), (0, −5) mm | 100, 500 | 36 / 6 |
| **I2** correction look-up | inj. 80 MeV; ext. aligned | 5, 10, 15, 20, 25 mm | 0 | power | 20, 50, 80, 100, 150, 200, 250, 300, 400, 500 | 240 / 6 |
| **I3** single bunch | inj. 25; ext. 10; inj. 10 mm | ref. | 0 | `SingleBunch` tracking beam (`single aligned` at extraction — same −4σₜ as generation, not −204.6 ns) | 100 | 9 / 3 |

I1 and I2 overlap at extraction (sizes 5–20 mm, 100–500 kW, 0 G); overlapping points are counted once, in I1. I3 extraction (10 mm, 100 kW, 0 G) is compared to the I1 aligned 3-bunch point, never to the v1 as-run extraction CSV.

### Timing contract (extraction ions)

The v1 artefact is a mismatch of two Virtual-IPM offsets, not a physics effect. Every v2 extraction ion XML must satisfy **generation-window centre = first tracking-bunch centre**. With σₜ = 20 ns that common centre is 80 ns (= 4σₜ).

| Beam | Generation (fields off) | Tracking train | First-bunch centre | Status |
|---|---|---|---|---|
| Injection, v1 and v2 | `SingleBunch`, default −4σₜ → 480 ns | `CircularBunchTrain`, `LongitudinalOffset` = −spacing/2 = −480 ns | 480 ns | already aligned; reuse |
| Extraction, v1 as-run | `SingleBunch`, default −4σₜ → 80 ns | `CircularBunchTrain`, `LongitudinalOffset` = −204.6 ns | 204.6 ns | **125 ns lag; do not reuse** |
| Extraction, I1 / I2 | same 80 ns | `CircularBunchTrain`, `LongitudinalOffset` = **−80 ns** (= −4σₜ), slug `aligned` | 80 ns | the fix |
| Extraction, I3 | same 80 ns | `SingleBunch` with **no** `LongitudinalOffset` (default −4σₜ). Must not copy `BEAMS["extraction"]["offset_ns"]` = −204.6 | 80 ns | `train = single aligned` |

Acceptance check before any XML is written (generator hook 2): print both centres; abort if they differ by more than 1 ns. The two equivalent fixes of review §3.5 (move the train, or move the generation bunch) are not mixed: v2 always keeps generation at the default −4σₜ and moves the tracking train.

v1 as-run extraction CSVs stay on disk as the mis-timed reference. They are never the baseline for I1–I3, never a reuse hit, and never the look-up column of the §3.7 correction recipe.

## 4. Run counts (`python3 scripts/scan_matrix_v2.py`)

| Block | Description | Runs | Reused | New |
|---|---|---:|---:|---:|
| E1 | ramp / β scan, 6 energies × 2 σₜ, 10 mm, 6 B, 100/500 kW | 216 | 30 | 186 |
| E3 | phase-aware B grid × V (10–30 kV), ext. 10 mm + inj. 25 mm | 336 | 0 | 336 |
| E4 | low power 20/50/80 kW, 3 reference beams, 5 B | 45 | 0 | 45 |
| I1 | aligned extraction: sizes × 5 P × 2 B, V scan, 3 offsets | 269 | 0 | 269 |
| I2 | look-up h(σ₀, N, species): 5 σ × 10 P, inj. + aligned ext. | 246 | 80 | 166 |
| I3 | single bunch vs 3-bunch; extraction is `single aligned` | 12 | 0 | 12 |
| **Total** | | **1124** | **110** | **1014** |

Reused points are v1 runs that coincide exactly (E1: 80 MeV/120 ns and 1.6 GeV/20 ns at Block A fields; I2: injection sizes 5–25 mm at 100–500 kW). For comparison, v1 executed 8127 runs; v2 adds 12 % of that while closing every "partial" and "open" row of the review matrix that simulation can close.

**Suggested order.** I1 first (it corrects a known bias in published numbers of the report), then I2 (delivers the correction table), E1, E3, E4, I3.

## 5. Generator hooks required (not implemented)

The v1 generator `scripts/generate_csns_configs.py` needs five additions before v2 can be written; none of them changes an existing v1 config:

1. **Beam energy and bunch length as parameters** (E1): `beam_xml()` takes `energy`, `sigma_t_ns`, `spacing_ns`, `offset_ns` from the `BEAMS` dict; E1 needs them computed from β (T_rev = 227.92 m / βc) for the six energies and two σₜ values. Suggested family slug `ramp_e{energy_mev}mev_st{sigma_t_ns}ns_s10x10mm`.
2. **Aligned extraction ion timing** (I1, I2, I3): `ion_case()` today builds the tracking train with `circular_train(3, spacing, offset=-spacing/2)` (−204.6 ns at extraction). The aligned variant must pass `offset = -4·σₜ` (−80 ns) so the first bunch centre equals the generation-window centre (80 ns). Abort XML write if the two centres differ by more than 1 ns. New slug infix `aligned` so as-run and aligned CSVs never collide (`csns_extraction_{species}_aligned_s10mm_p100kw_b0G_sc_on.csv`). Do not implement the alternative of moving the generation bunch — one convention only.
3. **Single-bunch ion train** (I3): reuse `single_bunch_train()` (already used for generation, default −4σₜ) for the tracking beam. Do **not** attach `BEAMS["extraction"]["offset_ns"]` to a `SingleBunch` — that would recreate the 125 ns lag. Slug infix `single` (injection) / `single_aligned` (extraction). Compare I3 extraction to the I1 aligned 3-bunch point, not to the v1 as-run CSV.
4. **New power and field values**: `POWERS_KW` gains 20, 50, 80 (E4, I2) and 150, 250 (I2); `b_tag()` already handles arbitrary gauss values, so the phase grids (E3) need only `phase_grid_gs(V)` from `scan_matrix_v2.py`.
5. **Evaluators**: `evaluate_emode.py` / `evaluate_imode.py` group by family slug; the three new slugs (ramp, aligned, single) need family patterns and a `--from-summary` replot path like the existing ones. The threshold routine should add the lobe-envelope metric next to the strict "last excursion" threshold.

`scan_matrix_v2.py` is the single source of the point list; a future `--v2` flag of the generator should iterate over `output/csns_scan_matrix_v2.csv` rather than re-encode the loops.

## 6. Open inputs (not counted)

| Item | Needed from | Unblocks |
|---|---|---|
| Cage field map (CST or measured) | CSNS IPM hardware group | e-mode field-non-uniformity block (J-PARC 2× shrink is the reference) |
| Bunch length σₜ(t) along the ramp (WCM) | RCS operations | ramp-realistic E1 variant |
| Ion initial-momentum model in Virtual-IPM (thermal / dissociation energy) | Virtual-IPM feature check | §6 "ions at rest" assumption; otherwise add ≈ 1 mm in quadrature |
| MCP window 30 × 80 mm and gain model | IBIC'25 TUPMO41 geometry | detector-level widths at 500 kW / 3 mm (cage-limited today) |

## 7. Execution results

All 1014 new runs finished (4 parallel Virtual-IPM jobs). `scripts/evaluate_v2.py` pairs each SC-on CSV with its SC-off partner (v2 file, or the v1 file when the off point was reused). 735 SC-on pairs are in `output/csns_v2_summary.csv`. 78 pairs are unpaired because the matching v1 SC-off particle CSV is not on disk (I2 injection at 20/50/80/150/250 kW; E4 painted injection at 1000 G).

![Aligned extraction vs as-run and the kick model](plots/csns_v2_aligned_extraction.png)

**Figure.** Extraction 10 mm, 0 G, 100 kW, 25 kV. The v2 aligned Virtual-IPM expansions match the kick-model aligned column of the review (H₂⁺ +104 % vs +102 %; H₂O⁺ +41 % vs +40 %; N₂⁺ +40 % vs +39 %) and replace the v1 as-run lower bound (H₂⁺ +33.5 %).

| Check | Result |
|---|---|
| I1 timing contract | tracking `LongitudinalOffset` = −80 ns; first bunch at 80 ns |
| I1 aligned 10 mm / 100 kW / 0 G | H₂⁺ +104.1 %, H₂O⁺ +40.8 %, N₂⁺ +40.0 % |
| E4 80 kW at 300 G | inj. 25 mm +0.02 %, ext. 10 mm +0.18 %, inj. 10 mm +0.49 % |
| E1 300 G / 100 kW / σₜ = 120 ns | +0.42 % (200 MeV) → +0.24 % (1.6 GeV); 80 MeV is the reused v1 point |

Physics write-up: [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) (size growth §3, mitigation efficiency §4, Figure 11).

## Appendix

Rebuild the PDF: `python3 scripts/md_to_pdf.py --md SCAN_MATRIX_V2.md --pdf SCAN_MATRIX_V2.pdf --footer "CSNS RCS IPM — scan matrix v2 (plan)"`.
