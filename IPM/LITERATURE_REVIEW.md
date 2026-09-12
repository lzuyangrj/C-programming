# CSNS RCS IPM simulations — review against IPM publications (2006–2026)

**Scope.** This note checks the Virtual-IPM 2.3.1 results collected in [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) (electron mode, Blocks A–D + fine C/D; ion mode, Blocks A–D; scan matrix v2 I1–I3 / E1 / E3 / E4) against IPM design rules, measurements and simulation studies published in the last twenty years (2006–2026). Each comparison section states what the literature predicts for the CSNS parameters, what the simulations gave, and whether the two agree. A machine-by-machine survey of that period is in Section 4 and a block-by-block comparison matrix in Section 5. Reproduce the comparison figures with `python3 scripts/literature_compare.py` (summary CSVs only, no Virtual-IPM runs). V2 execution: [`SCAN_MATRIX_V2.md`](SCAN_MATRIX_V2.md) §7.

**CSNS parameters used throughout.** Cage 220 × 231 mm, 25 kV so E ≈ 108 kV/m, design B = 0.1 T; 7.8 × 10¹² p/bunch at 100 kW (∝ power), two bunches per turn; injection 80 MeV (β = 0.39, σₜ = 120 ns, revolution 1.96 µs), extraction 1.6 GeV (β = 0.93, σₜ = 20 ns, revolution 0.82 µs). Round beams σ = 25 mm (painted injection) or 10 mm.

---

## 1. Summary of the review

1. **Electron mode agrees with the field-scaling literature in trend and order of magnitude.** The 1 % thresholds found here (105–155 G painted injection, 185–240 G extraction, 190–290 G 10 mm injection) are 1.1–4× above the Vilsmeier–Sapinski–Storey minimum-field fit (PRAB 22, 052801), which was fitted for β ≥ 0.99 and a monotonic distortion. The oscillation of the distortion with B that drives this gap is the cyclotron phase of the space-charge kick: the zeros of Δ(B) are spaced by π m_e/(e · ToF) ∝ √V to within 5 % at every cage voltage of Fine C (Section 2.3). For σ = 3 mm and for σ ≥ 4 mm at 300 G the fit and the simulation agree directly (Section 2.4). The recommended 300 G matches the SNS ring IPM design point (300 G, ≈7 % estimated error for 2 × 10¹⁴ p) and sits well below the CSNS design (0.1 T) and the 0.2 T available magnet — the same field used by the CERN PS BGI (< 2.5 % distortion for LHC-type bunches).
2. **Ion mode agrees quantitatively with space-charge kick theory.** A reduced line-charge model of the type used by Shiltsev (NIM A 986 (2021) 164744) reproduces every 0 G / 100 kW Virtual-IPM expansion to within ±1 % absolute (Figure 2), the V⁻⁰·⁹ cage-voltage law matches the ISIS "broadening ∝ 1/drift field" result, and the flatness versus B follows from the cyclotron phase ω τ ≲ 1 rad accumulated during the ion flight. The size scaling (σ₀^−2, impulsive regime) and the ±5 mm vertical-offset dependence (σ_m² − σ₀² ∝ drift length) also follow the kick model to within 0.5 %. The ion-mode bias (+9 % to +92 % at 100 kW, up to +422 % at 500 kW) is of the size reported operationally at J-PARC RCS (IPM 20–30 % wider than the MWPM) and at the Fermilab Booster (correction ≈ 15 % to ≈ 2×).
3. **Two caveats surfaced by the review; the first is now closed.**
   - The **v1 extraction ion-mode configuration** generated ions 125 ns before the first field-carrying bunch (generation at 80 ns, tracking train at 204.6 ns). H₂⁺ therefore drifted ≈ 40 mm before the kick and the as-run expansion (+33.5 %) was a lower bound. Scan matrix v2 I1 re-ran extraction with tracking `LongitudinalOffset` = −80 ns: H₂⁺ **+104.1 %**, H₂O⁺ +40.8 %, N₂⁺ +40.0 % at 10 mm / 100 kW / 0 G, matching the aligned kick model (+102 / +40 / +39 %). Injection was already aligned (both centres at 480 ns). Section 3.5.
   - The simulations use **uniform** guiding fields and stop at the collector: no MCP, no ion trap, no field-cage non-uniformity, no secondary electrons. J-PARC reported that its RCS IPM profile was shrunk to half by external-field distortion alone, and the CSNS IBIC 2024–2026 papers describe MCP saturation after 200 µs and secondary-electron suppression as the dominant hardware issues. These effects, not space charge, currently limit the CSNS e-mode measurement.
4. **Recommendation unchanged, now literature-backed:** run the CSNS RCS IPM in electron mode with B ≳ 300 G (the design 0.1 T is conservative up to 500 kW and σ = 3 mm), and treat ion-mode sizes as space-charge biased. A species-resolved correction of the Shiltsev / ISIS type is feasible for CSNS because the ToF peaks (H₂⁺, H₂O⁺, N₂⁺) are resolved and the bunch charge is known turn by turn.

---

## 2. Electron mode

### 2.1 Minimum guiding field: Vilsmeier, Sapinski, Storey, PRAB 22, 052801 (2019)

The paper derives, from Virtual-IPM scans over 0.2–20 mm, 0.3–300 ns and 10⁹–10¹³ charges (relativistic beams, β ≥ 0.99), the minimum field for a ≤ 1 % increase of the measured RMS width,

B_min,1% [T] = d · N^a / (σ_z^b · σ_t^c) + f / σ_t^e, with (a, b, c, d, e, f) = (0.613, 0.590, 1.082, 0.105, 0.967, 0.038) for Gaussian bunches; N in 10¹², σ_z in ns, σ_t in mm.

The first term is the space-charge term, the second the initial-velocity (gyroradius) term. The fit reproduces the SIS100 design (76 mT predicted vs 84 mT foreseen).

![Virtual-IPM 1% thresholds vs the PRAB fit](plots/csns_review_emode_bmin.png)

**Figure 1.** Block A 1 % thresholds (points: smallest B after which |Δ| ≤ 1 % for the rest of the 0–300 G grid) compared with Eq. (8) (dashed) and Eq. (8) with N replaced by N/β to account for the longer field exposure of a slow beam (dotted).

| Family | Power | Virtual-IPM | Eq. (8) | Eq. (8), N/β |
|---|---:|---:|---:|---:|
| Inj. 25 mm | 100 kW | 105 G | 24 G | 29 G |
| Inj. 25 mm | 500 kW | 155 G | 35 G | 49 G |
| Inj. 10 mm | 100 kW | 210 G | 59 G | 73 G |
| Inj. 10 mm | 500 kW | 190 G | 90 G | 128 G |
| Ext. 10 mm | 100 kW | 240 G | 93 G | 96 G |
| Ext. 10 mm | 500 kW | 205 G | 181 G | 188 G |

**Assessment.** The ordering of the families and the absolute scale (tens to a few hundred gauss, far below the LHC-type 0.2–0.5 T regime) agree. The simulated thresholds exceed the fit by 1.1× (extraction, 500 kW) to 4× (painted injection). Three reasons are identifiable:

- **Threshold definition.** Our curves oscillate in sign with B (focusing vs over-kick of the electron, Figures 1–2 and 6 of the report). "Last B at which |Δ| leaves the ±1 % band" is stricter than the monotonic σ_m/σ_t − 1 = τ used for the fit; a single excursion at, e.g., 285 G sets the 10 mm / 200 kW threshold to 290 G although 200–280 G are already inside the band.
- **Low β.** At 80 MeV the electrons stay in the bunch field 2.5× longer than for β ≈ 1 and the longitudinal bunch field is no longer negligible; the paper restricts its fit to β ≥ 0.99 for precisely this reason. The N/β column recovers part of the gap at injection but not all of it.
- **Weak power dependence.** The fit scales as N^0.61 (×2.7 between 100 and 500 kW) whereas the simulated thresholds are flat or even decrease with power (10 mm injection 210 → 190 G). This is the same oscillatory mechanism: a stronger kick moves the first over-focusing peak to a different B rather than just raising the distortion, so a monotone power law cannot be expected.

The initial-velocity term of the fit (0.038/σ_t^0.967 T) alone gives 17 G (25 mm), 41 G (10 mm) and 131 G (3 mm); with the space-charge term the full fit gives 200 G (injection) and 320 G (extraction) for σ = 3 mm at 100 kW. This is why in Block B the 3 mm beams stay at +1.0 / +1.5 % at 300 G and only 0.1 T brings them onto the diagonal — for the smallest beams the fit and the simulation agree. The 0.1 T CSNS design value is therefore the right order for the smallest beams, and 300 G is ample for σ ≥ 10 mm.

### 2.2 Distortion mechanisms

The report's B = 0 phenomenology (expansion at low V, compression above 13 kV at 100 kW, never-flipping expansion at 500 kW) maps onto the regimes described in the PRAB paper and in the early SNS design notes:

- **Trapping when the bunch field exceeds the extraction field.** Peak transverse bunch fields for the CSNS cases (2D Gaussian line charge): 12 kV/m (inj. 25 mm), 29 kV/m (inj. 10 mm), 73 kV/m (ext. 10 mm) at 100 kW; 145 and 363 kV/m for the 10 mm beams at 500 kW. The cage field is 108 kV/m. At 500 kW the extraction bunch field exceeds the cage field around 1–2 σ, i.e. the electrons are trapped in the beam potential during the bunch passage — the situation the PRAB paper identifies as needing B rather than V. This is the origin of the "500 kW never flips" observation in Block C.
- **Polarisation drift and gyroradius increase.** With B on, the paper describes the distortion as a gyroradius increase plus an E × B / polarisation drift; roughly 90 % of the electrons end up with larger gyroradii. In our 5 G scans this shows as the damped oscillation of Δ with B whose period lengthens as V rises (later first peak in Fine C), consistent with the electron time-of-flight setting the number of gyrations performed inside the bunch field. Section 2.3 makes this quantitative.
- **Sign reversal with intensity.** At 25 kV and 0 G the 10 mm injection profile is *compressed* by 48 % at 100 kW but *expanded* by 80 % at 500 kW. Electrons are attracted towards the positive bunch, so a moderate kick focuses them; once the bunch field exceeds the cage field they cross the axis and oscillate in the bunch potential, and the collected profile is wider than the beam. GSI (DIPAC'11) reports the same sign rule — "ions broaden, electrons shrink without B" — for its moderate-intensity beams, and J-PARC (HB2010) a 2× shrunk e-mode profile; the CSNS 500 kW case is the over-focused continuation of the same curve.

### 2.3 Cyclotron-phase check of the B oscillation (Fine C)

If the space-charge kick is delivered early in the electron flight (the electron leaves the 10 mm beam in ≈ 1 ns of its 3.5 ns ToF), its transverse displacement at the collector is (Δv/ω_c) · sin(ω_c τ) and vanishes whenever ω_c · ToF = nπ. Successive zero crossings of Δ(B) are then spaced by ΔB = π m_e / (e · ToF), with ToF = √(2 d m_e / (eE)) ∝ 1/√V (d = 115.5 mm, E = V / 231 mm). Fine C (injection 10 mm, 100 kW, 5 G steps) gives:

| Cage voltage | ToF | ΔB predicted | ΔB, Fine C zeros |
|---:|---:|---:|---:|
| 10 kV | 5.51 ns | 32.4 G | 30.9 G (10 zeros) |
| 15 kV | 4.50 ns | 39.7 G | 39.1 G (7) |
| 20 kV | 3.89 ns | 45.9 G | 45.7 G (6) |
| 25 kV | 3.48 ns | 51.3 G | 51.7 G (5) |
| 30 kV | 3.18 ns | 56.2 G | 55.1 G (5) |

![Cyclotron-phase check](plots/csns_review_emode_cyclotron.png)

**Figure 3.** Left: Fine C expansion vs B at 10 and 25 kV (100 kW) with the predicted zeros n · π m_e/(e · ToF) as dotted lines. Right: spacing between zero crossings vs cage voltage against π m_e/(e · ToF) ∝ √V.

**Assessment.** The measured spacing follows the √V law to within 5 % at every voltage, with no free parameter. This confirms (i) that the oscillatory Δ(B) in Blocks A and C and in Fine C is the cyclotron phase of a quasi-impulsive kick, as described qualitatively in PRAB 22, 052801 and in the GSI/J-PARC "one gyration" tuning rule, and (ii) why the 1 % threshold cannot follow a monotone N^0.61 law: the envelope of the oscillation decays with B while its zeros move with V, so the last excursion beyond ±1 % (our threshold definition) jumps between lobes. At 25 kV the lobes are at 85, 140, 195, 240, 295 G with amplitudes 12.8, −3.9, 1.4, −0.9, 0.6 %; 300 G is the first field at which the envelope is ≤ 1 % for all powers, which is the origin of the recommendation. The same phase also explains the SC-off result of Block B: at 100 G the electron performs 0.98 gyrations in 3.5 ns, so the initial-velocity smear of 3.2 mm at 0 G collapses to 0.08 mm rms (measured 0.077 mm), independent of σ.

### 2.4 Beam size and the initial-velocity term (Block B)

- **Initial-velocity smear.** With space charge off and B = 0 the collected width exceeds the beam width by a σ-independent quadrature term σ_v = 3.24 ± 0.01 mm (extraction) and 2.91 ± 0.03 mm (injection), i.e. +48 % / +40 % at σ = 3 mm and +1.3 % / +1.0 % at 20 mm. Divided by the 3.5 ns ToF this is v_rms = 0.93 / 0.83 × 10⁶ m/s, or 2.5 / 2.0 eV per transverse axis — the low-energy peak of the Voitkiv H₂ DDCS used by both Virtual-IPM and the PRAB paper; the dependence on β (extraction electrons slightly hotter) is the expected DDCS projectile-velocity dependence.
- **Vilsmeier initial-velocity term.** f/σ_t^e = 131 G (3 mm), 41 G (10 mm), 21 G (20 mm), 17 G (25 mm). Because the CSNS ToF is close to one cyclotron period at 100 G (Section 2.3), the SC-off residual is already 0.02–0.06 % at 100 G and ≤ 0.16 % at 300 G for every σ from 3 to 20 mm, well inside the fit's 1 % criterion; the fit was derived for a different gap/voltage and is conservative for CSNS.
- **Residual space-charge distortion vs σ.** At 300 G and 100 kW the SC-on expansion stays within −0.34 … +1.53 % (extraction) and +0.09 … +0.98 % (injection) for 3 ≤ σ ≤ 20 mm, with the largest values at 3 mm; at 0.1 T all values are ≤ 0.05 %. The full PRAB fit gives B_min,1% = 320 G (extraction) and 200 G (injection) for 3 mm at 100 kW, so a residual just above 1 % at 300 G for the extraction beam and just below for injection is exactly what the fit predicts. For σ ≥ 4 mm the fit (≤ 240 G) and the simulation (|Δ| ≤ 0.5 % at 300 G) agree as well; the 3 mm extraction bunch field (peak ≈ 240 kV/m at 100 kW) exceeds the cage field, which is why this is the only Block B case needing the full 0.1 T.

### 2.5 Beam offsets (Block D, Fine D)

- **Vertical offsets (towards / away from the collector), Δy = ±10 mm in 1 mm steps.** At 300 G the expansion stays within |Δ| ≤ 0.65 % for both beams and both powers, and at 0.1 T within 0.05 %; at 0 G the extraction expansion changes by 0.85 % per mm (24.6 % at −10 mm to 41.7 % at +10 mm, 100 kW) because the electron stays longer in the bunch field when the beam is farther from the collector. The PRAB fit and the SNS/J-PARC design notes assume a centred beam; for CSNS at ≥ 300 G the assumption costs < 1 %.
- **Centroid.** The space-charge-induced centroid shift along the measured axis is −0.89 / −0.37 / −0.24 / −0.07 mm at 100 / 200 / 300 / 1000 G (extraction, 100 kW), i.e. ∝ 1/B — the E × B / polarisation drift discussed in PRAB 22, 052801 — and roughly doubles at 500 kW (−0.59 mm at 300 G). It is independent of Δy to ± 0.02 mm and so is a fixed, correctable offset rather than a position error.

### 2.6 Machine comparisons

| Machine / paper | Beam and field | Reported distortion | CSNS this work |
|---|---|---|---|
| SNS ring IPM, Bartkoski & Deibele, NIM A 767 (2014) 379 | 2 × 10¹⁴ p, 120 kV bias, 300 G | ≈ 7 % estimated; an earlier ORNL note argued 250 G suffices, 0.1 T in the original design | 7.8 × 10¹² p (25× less charge) at 300 G: ≲ 1 % for all families, powers and offsets |
| J-PARC RCS IPM, Satou et al., HB2010 WEO1C05 | 4.5 × 10¹² p, ion mode operational; 3-pole wiggler for e-mode | ion mode 20–30 % wider than MWPM; e-mode without B dominated by contamination; profile shrunk 2× by external-field non-uniformity | same ion-mode magnitude (Section 3); uniform fields assumed, so the field-error effect is not modelled |
| CERN PS BGI, NIM A 1081 (2026) 170845 | LHC-type bunches, 200 mT, hybrid-pixel detection | < 2.5 % distortion in simulation | LHC-type bunches sit at the 0.2–0.5 T end of the PRAB scaling; CSNS bunches (long, wide) need 10× less |
| GSI SIS100 IPM (PRAB 22 example) | 2 × 10¹³, σ = 2.17 mm, σ_z = 15 ns, 84 mT | fit gives 76 mT | our 3 mm / 20 ns extraction case needs ≈ 0.1 T — same regime |
| CSNS RCS IPM, Rehman et al., NIM A 1092 (2026) 171809; IBIC'24 WEP18; IBIC'25 TUPMO41; IBIC'26 MOP026 | 220 × 231 mm cage, up to 30 kV after conditioning, magnet up to 0.2 T, MCP readout; ion and electron modes | MCP saturation after 200 µs at 80 kW; EMI; secondary electrons from ions hitting the cage in e-mode → slit ion trap | simulation covers space charge only; the recommended 300 G is 6× below the available 0.2 T |

**Assessment.** No published magnetic IPM operating at a comparable charge per bunch reports a distortion inconsistent with ours: the SNS design (300 G, 25× the charge) expected ≈ 7 %, so ≲ 1 % at CSNS is the expected scaling. The hardware issues reported for the CSNS IPM (saturation, EMI, secondary electrons) are outside the simulated physics and will dominate the e-mode systematic error once the guiding field is ≥ 300 G.

---

## 3. Ion mode

### 3.1 Kick-model theory: Shiltsev, NIM A 986 (2021) 164744; PRAB 24, 044001 (2021)

Shiltsev gives a closed-form description of the space-charge expansion in ion IPMs without a magnetic field. Two regimes matter here:

- **Long or frequent bunches** (bunch length or spacing ≲ ion transit times): σ_m = σ₀ · h with h ≈ 1 + 2.41 · (U_sc · D / (V₀ σ₀)) · √(d/σ₀) for a Gaussian beam, U_sc = J / (4πε₀ v_p) the beam space-charge potential. h is independent of the ion species. For the CSNS average current (1.3 A at injection, 3.1 A at extraction) U_sc ≈ 100 V and h − 1 ≈ 75 % (σ₀ = 10 mm) and 19 % (25 mm).
- **Short, rare bunches** (bunch ≪ τ₀ ≪ spacing): the ion receives an impulse Δvₓ = 2Ze²N_p/(4πε₀ β M c) · x₀/r₀² · (1 − exp(−r₀²/2σ₀²)) and drifts for the transit time τ₂ = √(2dM/(ZeE)). The expansion then adds in quadrature, depends on Z/M (displacement ∝ M^−1/2), and heavier ions are preferred.

CSNS characteristic times at 25 kV: τ₀ (time to leave the beam) = 74 / 221 / 275 ns and τ₂ (transit to the collector) = 210 / 631 / 787 ns for H₂⁺ / H₂O⁺ / N₂⁺. With σₜ = 120 ns and 980 ns spacing at injection and 20 ns / 409 ns at extraction, CSNS sits between the two regimes: bunches are rare (τ₂ < spacing for H₂⁺), the extraction bunch is impulsive, the injection bunch is not (σₜ > τ₀ for H₂⁺). The simulated species ordering reflects this: at injection H₂⁺ > H₂O⁺ > N₂⁺ (+92 / +65 / +56 %), compressed relative to the M^−1/2 law of the impulsive limit because the light ion leaves the beam during the 120 ns bunch.

### 3.2 Direct check with a reduced model

To test the Virtual-IPM numbers against this physics, `scripts/literature_compare.py` integrates the same equations numerically (ions at rest, uniform E_y, 2D Gaussian line-charge field of the bunch train with the Virtual-IPM bunch timing, no MCP, ions counted at the collector; 30 000 ions per case, ≈ 1 s each).

![Reduced model vs Virtual-IPM](plots/csns_review_imode_model.png)

**Figure 2.** Left: 0 G, 100 kW expansions for the three species and three reference beams, reduced model vs Virtual-IPM. Right: Block C cage-voltage scan at 0 G (points) with the reduced model (lines).

| Case (0 G, 100 kW) | H₂⁺ model / Virtual-IPM | H₂O⁺ | N₂⁺ |
|---|---:|---:|---:|
| Inj. 25 mm | +15.6 / +16.7 % | +10.1 / +10.4 % | +8.8 / +8.9 % |
| Inj. 10 mm | +91.2 / +92.0 % | +64.4 / +64.7 % | +55.1 / +56.3 % |
| Ext. 10 mm | +32.6 / +33.5 % | +55.4 / +55.6 % | +50.2 / +49.9 % |
| Inj. 10 mm, 5 → 30 kV | 391 / 395 % → 75 / 77 % | 226 / 227 % → 56 / 56 % | 220 / 221 % → 51 / 49 % |

**Assessment.** Agreement is within ±1 % absolute for every point, including the counter-intuitive extraction ordering (heavy ions more distorted than H₂⁺). The Virtual-IPM ion-mode numbers are therefore exactly what the space-charge kick physics of the configured beams predicts; there is no numerical artefact. The agreement also means the reduced model can serve as a fast correction curve generator (Section 3.7).

### 3.3 Cage voltage and beam power

- **ISIS** (Pine, Payne, Warsop et al., EPAC06 / DIPAC07 and later reviews): "transverse trajectory deflection, and thus beam broadening, should be proportional to the reciprocal of the drift field", confirmed experimentally and in CST + tracking simulations. A linear scaling correction removes most of the error for reasonably centred beams (within ≈ 10 mm of the axis). Our 0 G Block C gives expansion ∝ V⁻⁰·⁹² (H₂⁺) and V⁻⁰·⁷⁷ (H₂O⁺) over 5–30 kV — the 1/E law with the expected saturation for heavier, slower ions that see part of a second bunch at low V.
- **Shiltsev** h − 1 ∝ N/V₀: our 0.1 T power scan (H₂⁺, 10 mm) grows as P¹·¹² between 100 and 400 kW (+82 → +390 %) and then saturates on the cage (+422 % at 500 kW, obtained σ ≈ 52 mm of a 110 mm half-aperture). The slightly super-linear exponent is the second-order term of the kick expansion (σₘ² = σ₀² + κN + κ²N²/σ₀² · …).
- **J-PARC RCS prototype** (Satou et al., EPAC06 TUPCH065): ion-mode broadening ≈ 8 % at 10 kV on the KEK-PS test, estimated ≈ 50 % at the 150 kV/m J-PARC RCS design field for σ = 30 mm and a 250 ns bunch. **ESS** (Marroncle, Benedetti, Belloni et al., IBIC'23 WEP001; JINST 15 (2020) T05007) chose ion collection at 300 kV/m for 1.5 × 10⁹ p bunches: electrons fail the ±10 % width requirement at that field, while ions stay below 5 % for 90 MeV beams larger than 2 mm. Extrapolating our V⁻⁰·⁹ law, a 10 % bias for the 10 mm CSNS injection beam at 100 kW would need ≈ 380 kV across the cage — not a practical route; this is the quantitative reason the report recommends against using ion-mode widths without correction.

### 3.4 Why B does not help ions

Between 0 and 200 G every ion expansion changes by < 0.5 %, and 0.1 T lowers H₂⁺ by ≈ 10 % relative (92 → 82 %) but H₂O⁺/N₂⁺ by < 1 %. This is the cyclotron phase accumulated during the transit: ω_c τ₂ = 0.20 rad (H₂⁺, 200 G), 1.01 rad (H₂⁺, 0.1 T), 0.34 rad (H₂O⁺, 0.1 T), 0.27 rad (N₂⁺, 0.1 T). A transverse kick applied early in the flight is reduced by ≈ sin(ω τ)/(ω τ) = 0.84 for H₂⁺ at 0.1 T and 0.98–0.99 for the heavy ions, reproducing the simulated 92 → 82 %, 65 → 64 % and 56 → 56 %. Shiltsev's remark that ion IPMs are operated without magnets, and Vilsmeier's that magnetic confinement is an electron-mode tool, are both confirmed for CSNS: even the full 0.2 T magnet (ω τ ≈ 2 rad for H₂⁺) would not restore ion profiles.

### 3.5 Timing caveat in the extraction ion configuration

In `generate_csns_configs.py` the ions are generated by a single fields-off bunch (Virtual-IPM default longitudinal offset −4σₜ, so the generation window is centred at t = 4σₜ) and tracked in a three-bunch circular train whose `LongitudinalOffset` is −spacing/2. At injection both centres fall at 480 ns, so ions see on average half of their own bunch — the assumption Shiltsev makes and the reduced model reproduces. At extraction the generation window is centred at 80 ns but the first tracking bunch arrives at 204.6 ns:

- H₂⁺ has already moved ≈ 40 mm towards the collector when the bunch passes, so it receives a much weaker, mostly vertical kick. The reduced model with a time-aligned generation gives **≈ +100 %** for H₂⁺ at extraction (0 G, 100 kW) instead of the +33 % obtained.
- H₂O⁺ and N₂⁺ move only 3–4 mm in 125 ns and instead see the **whole** bunch rather than half of it; aligned generation gives ≈ +40 % for both instead of +56 / +50 %.

The qualitative conclusions (positive bias at every V, B, size and offset; no recovery by B) are unaffected. Scan matrix v2 I1 executed the recommended fix (tracking `LongitudinalOffset` = −80 ns; generation left at −4σₜ). No v1 100k CSV was overwritten.

Aligned vs as-run expansions at 0 G, 100 kW, 25 kV. Virtual-IPM as-run is v1; Virtual-IPM aligned is v2 I1:

| Species | Inj. 25 mm model / VIPM | Inj. 10 mm | Ext. 10 mm as-run (v1) | Ext. aligned model / v2 I1 |
|---|---:|---:|---:|---:|
| H₂⁺ | +15.6 / +16.7 % | +91.2 / +92.0 % | +32.6 / +33.5 % | +102 / **+104.1 %** |
| H₂O⁺ | +10.1 / +10.4 % | +64.4 / +64.7 % | +55.4 / +55.6 % | +40 / **+40.8 %** |
| N₂⁺ | +8.8 / +8.9 % | +55.1 / +56.3 % | +50.2 / +49.9 % | +39 / **+40.0 %** |

The as-run / model-aligned pair is written to `output/csns_imode_kick_model.csv` by `scripts/literature_compare.py`. The v2 measurement is in `output/csns_v2_summary.csv` and [`CSNS_IPM_REPORT.md`](CSNS_IPM_REPORT.md) §4.5. I3 shows why the heavy-ion as-run numbers were high: a single aligned bunch gives H₂O⁺ / N₂⁺ +35.7 / +28.5 % (they miss the second RF bucket); the 3-bunch aligned run restores +40.8 / +40.0 %.

### 3.6 Beam size and offset scaling (ion Blocks B and D)

- **Size.** Between σ₀ = 5 and 20 mm at 0 G / 100 kW the expansion falls as σ₀^−1.98 (H₂O⁺, inj.), σ₀^−2.01 (N₂⁺, inj.), σ₀^−1.92 / σ₀^−1.87 (H₂O⁺ / N₂⁺, ext.) and σ₀^−1.84 (H₂⁺, inj.). Shiltsev's impulsive kick Δvₓ ∝ x₀/σ₀² gives h − 1 ∝ N/σ₀² in the linear regime, i.e. exponent −2, whereas the continuous (long-bunch) regime gives σ₀^−1.5. CSNS heavy ions are therefore firmly in the impulsive regime even at injection (τ₀ = 220–275 ns > σₜ = 120 ns); H₂⁺ at injection (−1.84) starts to feel the finite bunch length, and the mis-timed extraction H₂⁺ (σ₀^−0.91, Section 3.5) does not follow either law because the ion has already left the beam when the kick arrives. At 3 mm the expansions reach +480 to +840 % (mis-timed extraction H₂⁺: +70 %), the ion-mode equivalent of the "500 kW never flips" e-mode result: the profile fills the cage.
- **Vertical offset.** Moving the beam Δy = ±5 mm changes the ion drift length d = 115.5 mm and thus the transit time τ₂ ∝ √d. With σ_m² − σ₀² ∝ τ₂² ∝ d the predicted expansions for all six species/beam cases agree with Virtual-IPM to within 0.5 % absolute (e.g. H₂⁺ injection: 89.2 / 92.0 / 94.7 % simulated vs 88.9 / — / 95.0 % predicted for Δy = −5 / 0 / +5 mm; H₂O⁺ extraction 54.0 / 55.6 / 57.2 vs 53.6 / — / 57.6 %). Shiltsev's √(d/σ₀) factor in h is the same dependence in the continuous limit. The ion centroid does not move (< 0.02 mm).
- **Horizontal offset.** Δx = 5 and 10 mm along the measured axis leaves the expansion unchanged to 0.1 % at 100 kW for all species and the centroid within 0.01 mm: the kick is centred on the beam, so the ISIS statement that a linear scaling correction holds "within ≈ 10 mm of the axis" is reproduced. At 500 kW the H₂⁺ centroid is pulled back by −2.0 / −4.1 mm for Δx = 5 / 10 mm because the +420 % profile (σ_m ≈ 52 mm) is clipped asymmetrically by the 110 mm half-cage; this is an aperture effect, not space charge, and would appear as a position error in an uncorrected ion-mode measurement at high power.

### 3.7 Correction strategies in the literature

- **Analytic inversion (Fermilab Booster).** Shiltsev inverts σ_m = σ₀ h(σ₀, N, V₀, D, d) turn by turn using the DCCT intensity; the correction is ≈ 15 % early in the cycle and ≈ 2× at 8 GeV, and reaches 5–10 % accuracy on σ₀. CSNS has the same inputs (bunch charge, cage voltage, geometry) plus species-resolved ToF peaks, so a per-species inversion is possible. Because CSNS is in the mixed regime (Section 3.1), the inversion should use a numerically generated h(σ₀, N, V, species) table — the reduced model or Virtual-IPM itself — rather than the closed form.

  **Practical recipe for CSNS ion-mode widths.** Identify the ToF peak (H₂⁺ / H₂O⁺ / N₂⁺). Read the measured RMS σ_m and the DCCT bunch charge N. Look up or interpolate h(σ₀, N, V, species) from `output/csns_v2_summary.csv` (I1 / I2, aligned extraction) or `output/csns_imode_kick_model.csv` and solve σ_m = σ₀ · (1 + h) by a few substitutions, starting from σ₀ = σ_m. Use the **aligned** extraction column (v2 I1: H₂⁺ +104.1 % at 10 mm / 100 kW / 0 G), not the v1 as-run +33.5 %. Do not apply the e-mode 300 G knob to ions.
- **Tracking-based correction (ISIS).** CST field maps plus in-house tracking give correction factors for the measured percentage widths; a linear scaling is enough for reasonably centred beams. The same approach with the real (non-uniform) CSNS cage field is the natural next step once the field map is available.
- **Machine learning (PRAB 22, 052801; IBIC'17 WEPCC06; IPAC'18 WEPAK008; HB'18 THA2WE02).** Regressors trained on simulated distorted profiles reconstruct either the RMS width or the full shape. For CSNS this is optional: at ≥ 300 G the e-mode profile is already within 1 %, and the ion-mode bias is large but smooth in σ₀, N and V, so a look-up inversion suffices.

---

## 4. Twenty-year survey (2006–2026)

The last two decades of IPM work fall into three overlapping threads: **magnetic electron collection** as the high-intensity default, **analytic or ML correction** of residual ion-mode (and weak-B electron-mode) distortion, and **detector / vacuum engineering** (MCP ageing, EMI, ion traps, hybrid pixels). The CSNS RCS IPM sits in all three. RHIC (1999–2001, 0.12 T, strip anodes) is the immediate ancestor of the magnetic electron-mode design used at Tevatron, SNS, LHC/SPS and CSNS.

| Year | Facility and result | Relation to this work |
|---|---|---|
| 2006 | J-PARC RCS prototype (EPAC06 TUPCH065). Ion +8 % at 10 kV on KEK-PS; ≈ 50 % predicted at 150 kV/m (σ = 30 mm, 250 ns). 3-pole wiggler for e-mode. | Same ion physics; our 10 mm / 100 kW expansions are +56 to +92 % at higher charge density. |
| 2006–11 | Fermilab Tevatron Mk3: e-mode, 0.1–0.2 T, 10 kV / 63 mm. ISIS RCS/EPB: ion mode, no B, up to 60 kV; broadening ∝ 1/E (EPAC06, DIPAC07). | Tevatron B is the CSNS magnet class. ISIS 1/E law is Block C. |
| 2009 | CSNS RCS design (PAC'09 TH5RFP022): e-mode, 0.1 T, ~24 kV. | Design point of this campaign. |
| 2010 | J-PARC RCS/MR (HB2010 WEO1C05). Ion IPM 20–30 % wider than MWPM; e-mode without B contaminated; RCS profile shrunk 2× by field error. | Ion bias matches Block A. Field error is the largest un-modelled e-mode systematic. |
| 2011 | GSI SIS18 / ESR / COSY (DIPAC11 TUPD51). ~80 mT for e-mode; ions broaden, electrons shrink without B; MCP+P47 optical readout. | Same B = 0 sign rule as our voltage scan. |
| 2012 | LHC BGI (IBIC'12 TUPB61). e-mode (Ne), 0.2 T. Matches wire scanner at injection; larger than WS at 4 TeV; MCP ageing. | LHC bunches sit at the high-B end of the PRAB scaling; CSNS bunches are 10× longer and wider. |
| 2014 | SNS ring (NIM A 767 379). e-mode, 300 G, 120 kV; ≈ 7 % estimated error at 2 × 10¹⁴ p. | 300 G is our recommended point; CSNS has 25× less charge so ≲ 1 % is the expected scaling. |
| 2016 | J-PARC MR (IBIC'16 WEPG69). 0.2 T C+H magnet required for 30 GeV fast-extraction bunches. | CSNS magnet can reach the same 0.2 T. |
| 2016–18 | IPM simulation workshops (CERN, GSI, J-PARC); Virtual-IPM, IBIC'17 WEPCC07. | This is the code used here. |
| 2017 | CERN PS Timepix3 BGI (JINST 12 C02050), 0.2 T. ARIES workshop: SPS/LHC BGI needs ≳ 1 T for nominal LHC beam in the SPS. | Detector is outside our simulation. Confirms CSNS (long, wide bunches) is a 0.03 T problem, not a 1 T problem. |
| 2019 | Vilsmeier, Sapinski, Storey, PRAB 22 052801. B_min,1% scaling (Eq. 8); ML reconstruction. | Section 2.1; our thresholds are 1.1–4× the fit. |
| 2020 | ESS cold linac NPM (JINST 15 T05007; IBIC'23 WEP001). Ion mode at 300 kV/m; electrons fail the ±10 % width spec; ions < 5 % at 90 MeV, σ > 2 mm, 1.5 × 10⁹ p. | Opposite conclusion to CSNS because ESS bunches are 5000× emptier — ion mode only works at low N. |
| 2020–21 | Shiltsev, NIM A 986 164744; PRAB 24 044001; IBIC'21 TUPP05. Closed-form ion expansion h; 5–10 % inversion of Booster σ₀. | Section 3; reduced model agrees with Virtual-IPM to ±1 %. |
| 2024–26 | CSNS RCS IPM commissioning (IBIC'24 WEP18, IBIC'25 TUPMO41, NIM A 1092 171809, IBIC'26 MOP026). EMI, MCP saturation after 200 µs at 80 kW; ToF peaks H₂ / H₂O / N₂; slit ion trap. | Hardware, not space charge, currently limits the e-mode measurement. |
| 2026 | CERN PS BGI (NIM A 1081 170845). e-mode, 200 mT, Timepix; < 2.5 % size distortion in simulation. | Same B as the CSNS magnet; LHC-type bunches. |

**What changed over twenty years, and what did not.** Every high-intensity hadron machine that published an IPM paper in this period ended in the same place: collect electrons and apply B ≳ a few hundred gauss to a tesla, or collect ions and correct. The quantitative B needed is set by bunch charge, length and width (PRAB 22), not by a universal "0.2 T" rule — LHC/SPS sit at the tesla end, CSNS/SNS/J-PARC RCS at a few hundred gauss, SIS100 at ~80 mT. Ion-mode corrections matured from ISIS's empirical 1/E law (2006) to Shiltsev's closed form (2020) to ML on simulated profiles (2017–2019). Detector work moved from MCP+strips (RHIC, Tevatron, J-PARC) through MCP+phosphor+camera (LHC, GSI) to hybrid pixels (PS BGI) and, at CSNS, a gated cage plus an ion trap — none of which is in the present tracking.

---

## 5. Comparison matrix

Every simulated block is listed against the published prediction it was checked with. "Verdict" uses: **agrees** (quantitative, within the stated tolerance), **consistent** (same sign, order of magnitude or trend, no closed-form prediction), **partial** (agreement with an identified reason for the residual), **open** (no published benchmark, or the check needs data not in this campaign). Numbers are 100 kW unless stated.

**Electron mode**

| Simulated result | Literature prediction | Virtual-IPM | Verdict |
|---|---|---|---|
| Block A: 1 % threshold, 6 families (§2.1) | PRAB 22 Eq. (8): 24–181 G | 105–290 G | partial — 1.1–4×, oscillatory threshold definition and β < 0.99 |
| Block A: threshold vs power (§2.1) | Eq. (8): ∝ N^0.61, ×2.7 for 100 → 500 kW | flat or falling (210 → 190 G) | partial — lobe structure, not a monotone law |
| Block A/C: trapping at 500 kW (§2.2) | electrons trapped when E_bunch > E_cage | 145–363 kV/m vs 108 kV/m; never flips | consistent |
| Block C, 0 G: sign vs intensity (§2.2) | GSI DIPAC'11: electrons shrink without B; J-PARC HB2010: 2× shrink | −48 % (100 kW) → +80 % (500 kW) | consistent |
| Fine C: zeros of Δ(B) (§2.3) | ΔB = π m_e/(e ToF) ∝ √V, no free parameter | 30.9 / 39.1 / 45.7 / 51.7 / 55.1 G vs 32.4 / 39.7 / 45.9 / 51.3 / 56.2 G | agrees, ≤ 5 % |
| Block B, SC-off 0 G smear (§2.4) | Voitkiv DDCS: few-eV electrons | σ_v = 2.9 / 3.2 mm ⇒ 2.0 / 2.5 eV per axis | consistent |
| Block B, SC-off with B (§2.4) | Eq. (8) initial-velocity term 17–131 G | ≤ 0.16 % at 300 G for all σ; 0.077 mm rms at 100 G = (v/ω) sin(ω ToF) | agrees |
| Block B, 3 mm at 300 G (§2.4) | Eq. (8): 320 G (ext.), 200 G (inj.) | +1.5 % (ext.), +1.0 % (inj.) at 300 G; ≤ 0.05 % at 0.1 T | agrees |
| Block B, σ ≥ 4 mm at 300 G (§2.4) | Eq. (8): ≤ 240 G | Δ within ±0.5 % | agrees |
| Fine D: Δy = ±10 mm at 300 G (§2.5) | centred-beam assumption (PRAB, SNS) | Δ within ±0.65 %; 0.85 %/mm at 0 G | agrees — assumption costs < 1 % |
| Fine D: centroid shift (§2.5) | E × B / polarisation drift ∝ 1/B | −0.89 / −0.37 / −0.24 / −0.07 mm at 100 / 200 / 300 / 1000 G | consistent |
| 300 G recommendation (§2.6) | SNS 300 G ≈ 7 % at 25× the charge; PS 200 mT < 2.5 % | ≲ 1 % all families | consistent |
| Field non-uniformity, MCP, secondaries (§2.6) | J-PARC 2× shrink; CSNS IBIC'24–26 | not modelled | open — needs the CSNS field map |
| Low-β / ramp E1 (§2.1) | none published for β ≈ 0.4 | 300 G stays ±0.5 % from 80 MeV to 1.6 GeV at σₜ = 120 and 20 ns; 0 G compression/inflation shrinks with β | consistent — 300 G recommendation holds along the ramp |

**Ion mode**

| Simulated result | Literature prediction | Virtual-IPM | Verdict |
|---|---|---|---|
| Block A, 0 G, 3 species × 3 beams (§3.2) | reduced line-charge kick model (Shiltsev-type) | 9 cases within ±1 % absolute | agrees |
| Block A: species ordering (§3.1) | impulsive: ∝ M^−1/2; continuous: species-independent | inj. +92 / +65 / +56 % (H₂⁺ / H₂O⁺ / N₂⁺) | consistent — mixed regime |
| Block C: cage voltage (§3.3) | ISIS: broadening ∝ 1/E | V^−0.92 (H₂⁺), V^−0.77 (H₂O⁺) | agrees |
| Block C: power (§3.3) | Shiltsev h − 1 ∝ N (+ second order) | P^1.12, saturating on the cage at 500 kW | agrees |
| Block A: B dependence (§3.4) | cyclotron phase ω_c τ₂ ≲ 1 rad ⇒ sin x / x | 92 → 82 % (H₂⁺, 0.1 T), < 1 % change for heavy ions | agrees |
| Block B: size (§3.6) | impulsive ⇒ σ₀^−2; continuous ⇒ σ₀^−1.5 | σ₀^−1.84 … −2.01 (aligned cases) | agrees — impulsive regime |
| Block D: Δy = ±5 mm (§3.6) | σ_m² − σ₀² ∝ d (τ₂ ∝ √d) | 6 cases within 0.5 % absolute | agrees |
| Block D: Δx = 5, 10 mm (§3.6) | ISIS: linear correction within 10 mm of axis | width unchanged (0.1 %), centroid < 0.01 mm at 100 kW; −2 / −4 mm aperture pull at 500 kW | agrees at 100 kW; aperture effect at 500 kW |
| Ext. H₂⁺ as-run v1 (§3.5) | aligned model: ≈ +100 % | +33.5 % (125 ns generation lag) | artefact — superseded |
| Ext. aligned v2 I1 (§3.5) | kick model +102 / +40 / +39 % | VIPM +104.1 / +40.8 / +40.0 % (H₂⁺ / H₂O⁺ / N₂⁺) | agrees |
| Ion-mode bias magnitude (§3.3) | J-PARC 20–30 % wider; Booster 15 % → 2× | +9 … +92 % (100 kW); up to +422 % (500 kW) | consistent |
| ESS ion-mode choice (§3.3) | ions < 5 % at 300 kV/m, 1.5 × 10⁹ p | 10 % bias would need ≈ 380 kV at CSNS | consistent — opposite conclusion because N differs by 5000× |
| Dissociation energy, MCP window (§6) | ≈ 1 mm quadrature (Shiltsev); 30 × 80 mm MCP | not modelled | open — negligible / detector-level |

The numbers behind the Fine C, Block B and ion Block B/D rows are written to `output/csns_review_scaling_checks.csv` by `python3 scripts/literature_compare.py --checks-only` (summary CSVs only).

**Reading the matrix.** Thirteen of the twenty-seven rows are quantitative agreements with a published or first-principles prediction, nine are consistent in sign and magnitude with operational reports, two are partial, one is a superseded configuration artefact, and the two open rows concern hardware that the tracking does not include (field map, detector). The two "partial" e-mode rows share one cause — the oscillatory Δ(B) that Section 2.3 now pins to the cyclotron phase. The extraction timing artefact of Section 3.5 is closed by v2 I1. The former open low-β row is now the E1 ramp (300 G holds).

---

## 6. Modelling assumptions versus the literature

| Assumption here | Literature practice | Impact |
|---|---|---|
| Uniform E and B in the cage | Vilsmeier: uniform; J-PARC: 3D field map needed (profile shrunk 2×); ISIS: CST maps | Field non-uniformity is the largest un-modelled e-mode systematic |
| Electron generation from the Voitkiv H₂ DDCS only | PRAB 22, 052801 and Virtual-IPM benchmarks use the same H₂ DDCS | Standard; N₂/H₂O electron spectra are not available in Virtual-IPM |
| Ions at rest (ZeroMomentum) | Shiltsev: dissociative ionization gives H⁺ a few eV → σ_T ≈ 1 mm smearing; ESS/J-PARC likewise ignore or add in quadrature | Adds ≲ 1 mm in quadrature; negligible against +9–90 % biases |
| Detected-particle RMS at the collector, no MCP, no detector window | PS BGI and CSNS papers model the detector explicitly (Geant4 / MCP gain) | Widths at 500 kW / 3 mm saturate on the 110 mm half-cage, not on the 30 × 80 mm MCP window of the real device |
| Single bunch (e-mode) / 3-bunch circular train (ion mode) | Shiltsev's (1 + 0.8 t_b/τ₀) correction for bunched beams; ISIS multi-turn ions | Correct for H₂⁺; heavy ions at extraction see up to two bunches, which the reduced model also includes |
| Space charge = Gaussian bunch E and boosted B | Vilsmeier: same, longitudinal field neglected for β ≈ 1 | At 80 MeV the longitudinal field is retained by Virtual-IPM; no published low-β benchmark exists to compare against |

---

## 7. References

Papers are grouped by laboratory. Within each group the order is chronological.

**CSNS.**
1. W. Huang et al., "Ionization beam profile monitor designed for CSNS", Proc. PAC'09, TH5RFP022.
2. M. A. Rehman et al., "Troubleshooting the ionization profile monitor (IPM) for CSNS 1.6 GeV RCS", Proc. IBIC'24, WEP18.
3. M. A. Rehman, Y. Guo, Z. Xu, X. Nie, M. Liu, B. Zhang, R. Yang, "Preliminary data analysis of an IPM prototype CSNS RCS", Proc. IBIC'25, TUPMO41.
4. M. A. Rehman et al., "Fast residual gas ionization profile monitor for bunch-by-bunch beam profile measurements in the CSNS rapid cycling synchrotron", Nucl. Instrum. Meth. A 1092 (2026) 171809.
5. Xiao, Liu, Rehman, Yang, "Optimization of the ion trap for secondary electron suppression in the CSNS RCS IPM", IBIC'26, MOP026.

**Theory, simulation and correction.**
6. D. Vilsmeier, "A modular framework for simulations of ionization profile monitors", M.Sc. thesis (2017); D. Vilsmeier, P. Forck, M. Sapinski, Proc. IBIC'17, WEPCC07 (Virtual-IPM).
7. R. Singh et al., "Simulation supported profile reconstruction with machine learning", Proc. IBIC'17, WEPCC06; D. Vilsmeier et al., Proc. IPAC'18, WEPAK008; M. Sapinski et al., Proc. HB'18, THA2WE02.
8. D. Vilsmeier, M. Sapinski, R. Storey, "Space-charge distortion of transverse profiles measured by electron-based ionization profile monitors and correction methods", Phys. Rev. Accel. Beams 22, 052801 (2019).
9. V. Shiltsev, "Space-charge effects in ionization beam profile monitors", Nucl. Instrum. Meth. A 986 (2021) 164744; V. Shiltsev et al., Phys. Rev. Accel. Beams 24, 044001 (2021); Proc. IPAC'21 WEPAB018; Proc. IBIC'21 TUPP05.

**Spallation / RCS machines.**
10. K. Satou et al., "A prototype of residual gas ionization profile monitor for J-PARC RCS", Proc. EPAC'06, TUPCH065; "IPM systems for J-PARC RCS and MR", Proc. HB2010, WEO1C05; Proc. IPAC'13 MOPME021.
11. K. Satou et al., "Profile measurement by the ionization profile monitor with 0.2 T magnet system in J-PARC MR", Proc. IBIC'16, WEPG69.
12. B. G. Pine, S. J. Payne, C. M. Warsop et al., ISIS IPM studies, Proc. EPAC'06 and DIPAC'07 (CST field maps, 1/E broadening).
13. D. A. Bartkoski, C. Deibele, Y. Polsky, "Design of an ionization profile monitor for the SNS accumulator ring", Nucl. Instrum. Meth. A 767 (2014) 379.
14. F. Benedetti, F. Belloni, J. Marroncle et al., ESS cold-linac NPM: JINST 15 (2020) T05007; EPJ Web Conf. (2020); J. Marroncle et al., Proc. IBIC'23, WEP001.

**Colliders and European rings.**
15. M. Sapinski et al., "The first experience with LHC beam gas ionization monitor", Proc. IBIC'12, TUPB61; J. Storey, ARIES IPM workshop summary (2017).
16. S. Levasseur et al., "Development of a rest gas ionisation profile monitor for the CERN Proton Synchrotron based on a Timepix3 pixel detector", JINST 12 (2017) C02050; "Detection of ionization electrons with hybrid pixel detectors…", Nucl. Instrum. Meth. A 1081 (2026) 170845.
17. P. Forck et al., "Ionization profile monitors — IPM @ GSI", Proc. DIPAC'11, TUPD51; SIS18 / SIS100 magnet notes (≈ 80–84 mT).
18. R. Connolly et al., RHIC IPM (PAC'99 / PAC'01) — 0.12 T electron collection, the design ancestor of Tevatron Mk3, SNS and LHC BGI.

## Appendix

Rebuild the PDF: `python3 scripts/md_to_pdf.py --md LITERATURE_REVIEW.md --pdf LITERATURE_REVIEW.pdf --footer "CSNS RCS IPM — literature review"`.
