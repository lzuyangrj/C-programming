# CSNS RCS IPM — Ion-mode scan results

**Code:** Virtual-IPM 2.3.1. **Reference:** NIMA **1092** (2026) 171809 (CSNS RCS IPM).  
**Campaign:** round-beam ion-mode matrix, **2070 / 2070** v1 runs complete, plus **v2 I1–I3** (aligned extraction).  
**Species:** H₂⁺ (2 u), H₂O⁺ (18 u), N₂⁺ (28 u) — the three ToF peaks in the paper.  
**Statistics:** 100000 secondaries per run; quoted \(\sigma\) is the RMS of **detected** \(x\).

This report summarises the ion-mode parameter scan parallel to the e-mode replan
(`REPORT.md` §8) and the fine C/D e-mode scan (§9). Combined e-mode + ion-mode
physics note: [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) / [`CSNS_IPM_REPORT.pdf`](CSNS_IPM_REPORT.pdf).
Literature comparison (2006–2026): [`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) / [`LITERATURE_REVIEW.pdf`](LITERATURE_REVIEW.pdf).
V2 plan and timing contract: [`SCAN_MATRIX_V2.md`](SCAN_MATRIX_V2.md).
Unlike e-mode, **no dense \(B\)-scan** was run: every
block uses only \(B_y \in \{0, 200, 1000\}\,\mathrm{G}\) (no guide / mid checkpoint /
design 0.1 T), because closed ion scans already showed expansion **flat** vs \(B\).

---

## 1. Scan matrix

| Block | What is scanned | Beams | \(\sigma_x=\sigma_y\) | \(B\) [G] | Power [kW] |
|---|---|---|---|---:|---|
| **A** | Reference beams | inj. 80 MeV; ext. 1.6 GeV; inj. 80 MeV | 25 / 10 / 10 mm | 0, 200, 1000 | 100–500 |
| **B** | Beam size | inj.; ext. | 3–20 mm (1 mm) | 0, 200, 1000 | 100–500 |
| **C** | Cage voltage | inj. only | 10 mm | 0, 200, 1000 | 100, 500 |
| **D** | Beam offset | inj.; ext. | 10 mm | 0, 200, 1000 | 100, 500 |

Common settings: round beams (\(\sigma_y=\sigma_x\)); ideal cage
\(E_y = -V/231\,\mathrm{mm}\) (ions collected at \(y_\min\)); circular 3-bunch train;
simulation 12 µs / 8000 Boris steps; \(N_b = 7.8\times10^{12}\times(P/100\,\mathrm{kW})\).
SC-off reference: H₂⁺ @ 100 kW only (mass-independent without bunch fields, shared).

Re-run: `./scripts/run_imode_replan.sh` · Evaluate: `python3 scripts/evaluate_imode.py`

---

## 2. Takeaways

1. **Guiding \(B\) does not fix ion-mode profiles.** Expansion is flat between 0 and
   200 G and changes only slightly at 0.1 T — opposite to e-mode, where 200–300 G
   restores the profile.
2. **Ion distortion scales with power and inversely with beam size.** At 0.1 T, H₂⁺
   injection at \(\sigma=10\,\mathrm{mm}\) goes from +82% (100 kW) to +422% (500 kW);
   at \(\sigma=3\,\mathrm{mm}\), 500 kW gives obtained \(\sigma \sim 56\,\mathrm{mm}\)
   (+1700%+) for all three species.
3. **Lighter ions expand more at injection.** At 0.1 T / 100 kW / \(\sigma=10\,\mathrm{mm}\):
   inj. H₂⁺ +82%, H₂O⁺ +64%, N₂⁺ +56%. At **aligned** extraction the 20 ns bunch is
   impulsive and H₂⁺ is the most distorted species (+104 % at 0 G, +89 % at 0.1 T);
   the v1 as-run extraction ordering (H₂⁺ +32 %, heavy ions +50–55 %) was a timing artefact.
4. **Cage voltage matters for ions (ToF / dwell time).** Expansion stays **positive**
   at every voltage — no e-mode-style sign flip. Higher \(V\) shortens drift and
   **reduces** the kick (H₂⁺ inj. 10 mm @ 1000 G: +198% at 5 kV → +70% at 30 kV).
5. **Beam offset:** \(\Delta x\) is translation-invariant; \(\Delta y\) (toward/away
   from the detector) changes expansion by a few percent.
6. **Extraction timing is aligned in v2 I1.** The v1 train arrived 125 ns late
   (generation at 80 ns, tracking at 204.6 ns). Re-running with tracking
   `LongitudinalOffset` = −80 ns gives H₂⁺ **+104.1 %**, H₂O⁺ +40.8 %, N₂⁺ +40.0 %
   at 10 mm / 100 kW / 0 G — matching the kick model (+102 / +40 / +39 %). Use
   those widths, not v1 as-run +33.5 %. Injection was already aligned. See
   [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) §§3–4 and
   [`LITERATURE_REVIEW.md`](LITERATURE_REVIEW.md) §3.5.

---

## 3. Block A — reference beams vs \(B\)

Three round reference beams at 0, 200, and 1000 G, all powers, all species.

![Block A: expansion vs B for reference beams](plots/csns_imode_bscan.png)

**Figure 1.** Profile expansion vs no-SC [%] for the three reference beams. Each
panel is one species; columns are painted injection (25×25 mm), extraction (10×10 mm),
and small injection (10×10 mm).

Expansion is **essentially independent of \(B\)** between 0 and 200 G (cyclotron
radii are metres). The 0.1 T point is sometimes slightly lower but never restores
the profile.

### Table 1 — expansion at 100 kW [%]

| Species | Inj. 25 mm 0 G | 200 G | 1000 G | Inj. 10 mm 0 G | 200 G | 1000 G | Ext. 10 mm 0 G† | 200 G† | 1000 G† |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H₂⁺ | +16.7 | +16.7 | +15.0 | +92.0 | +91.6 | +82.1 | +33.5† | +33.4† | +31.6† |
| H₂O⁺ | +10.4 | +10.4 | +10.2 | +64.7 | +64.7 | +63.8 | +55.6† | +55.6† | +54.9† |
| N₂⁺ | +8.9 | +8.9 | +8.9 | +56.3 | +56.2 | +55.7 | +49.9† | +49.9† | +49.5† |

† v1 as-run extraction (125 ns generation lag). **Superseded by v2 I1** (table below).
Painted injection (25 mm) matches the elliptical-beam §1 numbers (+16% H₂⁺).
Injection is correctly aligned in v1 (both centres at 480 ns).

Aligned extraction, 10 mm, 100 kW, 25 kV (v2 I1; tracking offset −80 ns):

| Species | 0 G aligned | 0.1 T aligned | v1 as-run 0 G | Kick model aligned |
|---|---:|---:|---:|---:|
| H₂⁺ | **+104.1 %** | +89.1 % | +33.5 % | +102 % |
| H₂O⁺ | **+40.8 %** | +40.1 % | +55.6 % | +40 % |
| N₂⁺ | **+40.0 %** | +39.6 % | +49.9 % | +39 % |

H₂⁺ at extraction is the most distorted species once timing is correct. At 500 kW,
0 G, aligned 10 mm: H₂⁺ +408 %, H₂O⁺ +243 %, N₂⁺ +235 %. Size / voltage / offset
and the single-bunch check: [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) §3.2.

---

## 4. Block B — beam-size scan (3–20 mm)

Size scan at 0, 200, and 1000 G; injection and extraction; 100–500 kW.

![Block B: true vs obtained beam size at 0.1 T](plots/csns_imode_size_obtained.png)

**Figure 2.** Obtained \(\sigma_x\) vs true \(\sigma_x\) at **0.1 T**, 100 kW.
Dashed line: obtained = true. Every point lies **above** the diagonal at all three
\(B\) fields — space charge always inflates the detected width.

![Block B: expansion vs beam size at 0.1 T and power](plots/csns_imode_size_expansion.png)

**Figure 3.** Expansion vs true \(\sigma_x\) at **0.1 T** for 100–500 kW. Smaller
beams and higher power give dramatically larger expansion. On the v1 as-run
extraction timing, injection looked worse than extraction for H₂⁺; after the v2
alignment, extraction H₂⁺ is larger than the v1 table (see §3).

### Table 2 — obtained size at \(\sigma_x = 10\,\mathrm{mm}\), 0.1 T, 100 kW

| Species | Injection | | Extraction† | |
|---|---:|---:|---:|---:|
| | obtained [mm] | expansion | obtained [mm] | expansion |
| H₂⁺ | 18.2 | +82% | 13.2 | +32% |
| H₂O⁺ | 16.4 | +64% | 15.5 | +55% |
| N₂⁺ | 15.5 | +56% | 15.0 | +50% |

† v1 as-run. Aligned 0.1 T / 100 kW / 10 mm: H₂⁺ 19.0 mm (+89 %), H₂O⁺ / N₂⁺ 14.0 mm (+40 %).

### Table 3 — H₂⁺ injection, \(\sigma=10\,\mathrm{mm}\), 0.1 T vs power

| 100 kW | 200 kW | 300 kW | 400 kW | 500 kW |
|---:|---:|---:|---:|---:|
| +82% (18.2 mm) | +175% (27.5 mm) | +279% (37.8 mm) | +390% (48.9 mm) | +422% (52.1 mm) |

Worst case in the matrix: **injection, \(\sigma=3\,\mathrm{mm}\), 500 kW, 0.1 T** —
obtained \(\sigma \approx 56\,\mathrm{mm}\) (+1700%+) for all three species (cage-wall
saturation).

---

## 5. Block C — cage voltage (5–30 kV)

Injection 10×10 mm; voltages 5, 10, 15, 20, 25, 30 kV; B = 0, 200, 1000 G;
100 and 500 kW.

![Block C: cage voltage scan](plots/csns_imode_voltage.png)

**Figure 4.** Expansion vs \(B\) for each cage voltage. Unlike e-mode Block C, ion
expansion **never changes sign** — it stays positive at every \(V\). Higher voltage
shortens ion drift time and reduces the integrated space-charge kick.

### Table 4 — H₂⁺ injection 10 mm, 100 kW, 0.1 T vs cage voltage

| 5 kV | 10 kV | 15 kV | 20 kV | 25 kV | 30 kV |
|---:|---:|---:|---:|---:|---:|
| +198% | +168% | +126% | +100% | +82% | +70% |

At 500 kW the same trend holds but at much higher expansion (+300%–800% range).

---

## 6. Block D — beam offset

Injection and extraction 10×10 mm; offsets (+5,0), (+10,0), (0,+5), (0,−5) mm;
B = 0, 200, 1000 G; 100 and 500 kW.

![Block D: beam offset scan](plots/csns_imode_offset.png)

**Figure 5.** Expansion vs \(B\) for each offset (100 kW). \(\Delta x = +5\) and
\(+10\,\mathrm{mm}\) give **identical expansion** to the centred beam (translation
invariance). \(\Delta y = \pm5\,\mathrm{mm}\) changes expansion by a few percent
(toward the detector: slightly less expansion).

### Table 5 — H₂⁺ injection 10 mm, 0.1 T, 100 kW vs offset

| centred | \(\Delta x=+5\) | \(\Delta x=+10\) | \(\Delta y=+5\) | \(\Delta y=-5\) |
|---:|---:|---:|---:|---:|
| +82.1% | +82.1% | +82.1% | +84.0% | +80.0% |

Centroid shift vs no-SC is \(\lesssim 0.6\,\mathrm{mm}\) at extraction, 500 kW.

---

## 7. Comparison with e-mode (round-beam replan)

| | E-mode (§8) | Ion-mode (this report) |
|---|---|---|
| Secondaries | electrons | H₂⁺ / H₂O⁺ / N₂⁺ |
| \(B\) grid | dense (5 G / 25 G) | **0, 200, 1000 G only** |
| Effect of \(B\) | oscillatory recovery; 300 G fixes profile | **flat**; no recovery |
| Cage voltage | sign flip at low \(B\) | always positive; \(V\) tunes magnitude |
| Beam offset | \(\Delta x\) invariant; \(\Delta y\) matters | same |
| Worst case | low \(B\), wrong polarity | small \(\sigma\), high \(P\); aligned extraction H₂⁺ or injection |
| Extraction ions | n/a | use v2 aligned widths (H₂⁺ +104 % at 0 G / 10 mm / 100 kW) |

**Practical implication:** tune the IPM guiding field and cage voltage for **faithful
electron profiles**; treat **ion-mode size measurements as space-charge biased** unless
a correction model is applied. Extraction ion widths must come from the aligned v2
table, not from v1 as-run +33.5 %.

---

## 8. Data products

| File | Contents |
|---|---|
| `output/csns_imode_bscan_summary.csv` | Block A (135 rows) |
| `output/csns_imode_size_summary.csv` | Block B (1620 rows) |
| `output/csns_imode_voltage_summary.csv` | Block C (108 rows) |
| `output/csns_imode_offset_summary.csv` | Block D (180 rows) |
| `output/csns_v2_summary.csv` | v2 I1–I3 (aligned extraction, look-up, single bunch) |
| `plots/csns_imode_*.png` | Figures 1–5 above |
| `plots/csns_v2_aligned_extraction.png` | Aligned vs as-run vs kick model |
| `configs/csns_rcs_ipm/imode/README.md` | v1 matrix specification |

CSV files under `output/imode/` and `output/v2/` (particle lists) are gitignored.

---

## Appendix — all ion-mode figures

**Fig. I-1.** Block A — reference beams vs \(B\).

![Fig. I-1](plots/csns_imode_bscan.png)

**Fig. I-2.** Block B — true vs obtained \(\sigma\) at 0, 200, 1000 G (100 kW).

![Fig. I-2](plots/csns_imode_size_obtained.png)

**Fig. I-3.** Block B — expansion vs \(\sigma\) at 0.1 T, 100–500 kW.

![Fig. I-3](plots/csns_imode_size_expansion.png)

**Fig. I-4.** Block C — cage voltage 5–30 kV, injection 10×10 mm.

![Fig. I-4](plots/csns_imode_voltage.png)

**Fig. I-5.** Block D — beam offset on 10×10 mm injection and extraction.

![Fig. I-5](plots/csns_imode_offset.png)

**Fig. I-6.** v2 I1 — aligned extraction vs as-run vs kick model (10 mm, 100 kW, 0 G).

![Fig. I-6](plots/csns_v2_aligned_extraction.png)

Rebuild this PDF: `python3 scripts/md_to_pdf.py --md IMODE_REPORT.md --pdf IMODE_REPORT.pdf --footer "CSNS RCS IPM — ion mode"`.
