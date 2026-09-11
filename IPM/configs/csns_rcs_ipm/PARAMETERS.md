# CSNS RCS IPM parameters

Source paper: M. A. Rehman et al., *Fast residual gas ionization profile monitor for bunch-by-bunch beam profile measurements in the CSNS rapid cycling synchrotron*, Nucl. Instrum. Methods A **1092** (2026) 171809, [doi:10.1016/j.nima.2026.171809](https://doi.org/10.1016/j.nima.2026.171809) (PII `S0168900226005358`).

Instrument numbers that the NIMA article uses are also tabulated in the cited IBIC notes ([IBIC’25 TUPMO41](https://inspirehep.net/files/690b938dae6c882c3e83bf74c141df94), [IBIC’24 WEP18](https://inspirehep.net/files/c312b633bfe3fed9410aaa582e089e02)). Cage E/B design values for the *ideal static field* assumption come from the CSNS IPM design ([PAC’09 TH5RFP022](https://proceedings.jacow.org/PAC2009/papers/th5rfp022.pdf)).

| Quantity | Value used | Notes |
|---|---|---|
| Injection / extraction energy | 80 MeV / 1.6 GeV | Table 1 |
| Protons per pulse | \(1.56\times10^{13}\) | 100 kW CSNS |
| Bunches | 2 | → \(7.8\times10^{12}\) per bunch |
| RMS bunch length | 120 ns (inj.) / 20 ns (ext.) | IBIC’25, same device |
| RF / bunch spacing | 1.02 MHz → 980 ns (inj.) | Two-bunch harmonic |
| Field-cage aperture | 220 mm × 231 mm | Collection gap 231 mm |
| Cage bias | 25 kV | \(E_y = V/d \approx 108\,\mathrm{kV/m}\) (~110 kV/m in the paper) |
| Guiding \(B\) (design study) | 0.1 T, parallel to \(E\) | PAC’09 cage design (1000 G) |
| Guiding \(B\) (scan) | 0, 50, 100, 200 G | \(1\,\mathrm{G}=10^{-4}\,\mathrm{T}\) → 0, 5, 10, 20 mT |
| Guiding \(B\) (e-mode fine) | 0–250 G, step 5 G | Closed high-resolution \(B\) reference (painted inj., extraction, 10 mm inj. at 100 kW; painted + extraction at 200–500 kW) |
| E-mode replan beams | **round**, \(\sigma_y=\sigma_x\) | All replan blocks; 25×25 inj., 10×10 ext. and inj., \(\sigma\times\sigma\) size scan |
| E-mode replan \(B\) scan | **0–300 G, step 5 G** | Inj. 25×25, ext. 10×10, inj. 10×10; 100–500 kW |
| E-mode replan size-scan \(B\) | 0, 100, 200, 300 G, 0.1 T | Checkpoints from the same grid plus the design field |
| Beam power scan | 100–500 kW | \(N_b \propto P\); 100 kW is \(7.8\times10^{12}\)/bunch |
| Ion-mode \(\sigma_x\) scan | 3–20 mm, step 1 mm | \(\sigma_y=0.8\,\sigma_x\); H₂⁺/H₂O⁺/N₂⁺; inj. and ext. |
| E-mode \(\sigma\) scan | 3–20 mm, step 1 mm | Round; at the size-scan \(B\) values; inj. and ext.; 100–500 kW |
| E-mode cage-voltage scan | 5–30 kV, step 5 kV | \(E_y=V/231\,\mathrm{mm}\) = 22–130 kV/m; inj. 10×10 mm; 0–300 G step 25 G + 0.1 T; 100 and 500 kW |
| E-mode beam-offset check | (+5, 0), (+10, 0), (0, +5), (0, −5) mm | `TransverseOffset`; inj. and ext. 10×10 mm; 0/100/200/300 G + 0.1 T; 100 and 500 kW |
| Fine C (complete) | 5–30 kV / 1 kV at 11 diagnostic \(B\); 5 G \(B\)-scan at 10/12/15/18/20 kV | Zero at 13 kV (100 kW, \(B=0\)); 300 G recovers all \(V\); `REPORT.md` §9 |
| Fine D (complete) | \(\Delta y=-10\ldots+10\,\mathrm{mm}\) / 1 mm at diagnostic \(B\); 5 G at \(\Delta y=\pm 5\,\mathrm{mm}\) | Nearly linear in \(\Delta y\); 1% \(B\)-threshold within ~10 G of centred |
| Injection \(\sigma\) (repeat) | 10 mm × 8 mm | Same 5:4 aspect as 25×20; \(\sigma_x=10\,\mathrm{mm}\) |
| Extraction RF / bunch spacing | 2.444 MHz → 409.2 ns | RCS \(h=2\); used for extraction ion trains |
| Transverse \(\sigma\) (inj.) | 25 mm × 20 mm | Painted beam; PAC’09 quotes \(E_{x,\mathrm{sc}}\approx20\,\mathrm{kV/m}\) at the IPM |
| Transverse \(\sigma\) (ext.) | 10 mm × 8 mm | Adiabatic damping of the painted beam |
| Residual gas (electrons) | Hydrogen (`VoitkivDDCS`) | Virtual-IPM DDCS only supports H/He; paper’s H₂ peak |
| Ions | H₂⁺, H₂O⁺, N₂⁺ at rest (`ZeroMomentum`) | Paper ToF: hydrogen, vapor, nitrogen |
| Ion rest masses | 2 u / 18 u / 28 u | Multiples of the proton mass |
| Simulated secondaries | **100000** | `NumberOfParticles` |

Space charge in Virtual-IPM is the beam `BunchElectricField` (`Gaussian`) plus the Lorentz-boosted beam \(B\). It is switched **off** with `ElectricFieldOFF` and `MagneticFieldOFF`. Guiding cage fields stay uniform in both cases.

Injection-ion profile expansion at 100 kW (same 100000-particle runs as `output/csns_space_charge_summary.csv`):

| Residual-gas ion | Rest mass | \(\sigma\) no SC | \(\sigma\) with SC | Expansion |
|---|---:|---:|---:|---:|
| H₂⁺ | 2 u | 24.955 mm | 29.003 mm | +16.22% |
| H₂O⁺ | 18 u | 24.955 mm | 27.773 mm | +11.30% |
| N₂⁺ | 28 u | 24.955 mm | 27.394 mm | +9.77% |

Guiding-\(B\) scan (0–200 G) at injection and extraction, e-mode and H₂⁺ ion-mode (`output/csns_bscan_summary.csv`):

| \(B\) [G] | Inj. e− | Ext. e− | Inj. H₂⁺ | Ext. H₂⁺ |
|---:|---:|---:|---:|---:|
| 0 | −19.37% | +47.30% | +18.05% | +31.00% |
| 50 | −6.21% | −8.42% | +18.05% | +31.00% |
| 100 | +1.37% | +10.05% | +18.03% | +30.99% |
| 200 | +0.15% | +0.82% | +17.98% | +30.93% |

200 G restores electron profiles; ion expansion is essentially independent of \(B\) in this range. Extraction H₂⁺ expands more than injection because the 1.6 GeV bunch is shorter (20 ns), smaller (10×8 mm), and more relativistic. The 0.1 T residual-gas ion numbers above use the PAC’09 design field and differ slightly from the 0–200 G ion scan for that reason.

Fine e-mode scan (0–200 G, step 5 G): \(|\Delta|<1\%\) thereafter at 110 G (injection 25×20 mm) and 200 G (extraction). Injection 10×8 mm e− is still +1.57% at 200 G.

Injection 10×8 mm repeat at 0.1 T (`output/csns_space_charge_summary_sig10.csv`):

| Residual-gas ion | \(\sigma\) no SC | \(\sigma\) with SC | Expansion |
|---|---:|---:|---:|
| e− | 10.00 mm | 10.00 mm | ~0% |
| H₂⁺ | 9.98 mm | 18.68 mm | +87.2% |
| H₂O⁺ | 9.98 mm | 16.91 mm | +69.5% |
| N₂⁺ | 9.98 mm | 16.08 mm | +61.1% |
