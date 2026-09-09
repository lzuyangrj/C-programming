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
| Guiding \(B\) | 0.1 T, parallel to \(E\) | Ideal static cage field (PAC’09 design) |
| Transverse \(\sigma\) (inj.) | 25 mm × 20 mm | Painted beam; PAC’09 quotes \(E_{x,\mathrm{sc}}\approx20\,\mathrm{kV/m}\) at the IPM |
| Transverse \(\sigma\) (ext.) | 10 mm × 8 mm | Adiabatic damping of the painted beam |
| Residual gas (electrons) | Hydrogen (`VoitkivDDCS`) | Virtual-IPM DDCS only supports H/He; paper’s H₂ peak |
| Ions | H₂⁺, H₂O⁺, N₂⁺ at rest (`ZeroMomentum`) | Paper ToF: hydrogen, vapor, nitrogen |
| Ion rest masses | 2 u / 18 u / 28 u | Multiples of the proton mass |
| Simulated secondaries | **100000** | `NumberOfParticles` |

Space charge in Virtual-IPM is the beam `BunchElectricField` (`Gaussian`) plus the Lorentz-boosted beam \(B\). It is switched **off** with `ElectricFieldOFF` and `MagneticFieldOFF`. Guiding cage fields stay uniform in both cases.
