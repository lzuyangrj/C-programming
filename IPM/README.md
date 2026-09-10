# IPM — Virtual-IPM simulations

CSNS RCS Ionization Profile Monitor simulations using [Virtual-IPM](https://ipmsim.gitlab.io/Virtual-IPM/index.html) 2.3.1.

**Results note:** [REPORT.md](REPORT.md) — brief write-up of the 100000-particle space-charge and \(B\)-scan studies.

Docs: [Introduction](https://ipmsim.gitlab.io/Virtual-IPM/introduction.html) · [Install](https://ipmsim.gitlab.io/Virtual-IPM/installation.html) · [Usage](https://ipmsim.gitlab.io/Virtual-IPM/usage.html) · [Examples](https://ipmsim.gitlab.io/Virtual-IPM/examples.html)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
virtual-ipm --version
```

Optional GUI (local desktop only):

```bash
pip install 'Virtual-IPM[GUI]'
virtual-ipm-gui
```

## CSNS RCS IPM — space-charge impact

Uses the CSNS RCS beam and IPM parameters from
[NIMA 1092 (2026) 171809](https://doi.org/10.1016/j.nima.2026.171809)
(ideal uniform cage \(E_y\approx 108\,\mathrm{kV/m}\), \(B_y=0.1\,\mathrm{T}\)).
Number of simulated secondaries: **100000** per run (`NumberOfParticles`).

```bash
./scripts/run_space_charge_study.sh
python scripts/evaluate_space_charge.py
```

Each case is run **with** and **without** beam space charge (`ElectricFieldOFF` / `MagneticFieldOFF`). Guiding fields stay uniform.

Results at 100 kW (\(7.8\times10^{12}\) protons/bunch), **100000** tracked particles, ideal \(E_y\) and \(B_y=0.1\,\mathrm{T}\). Residual-gas ions follow the paper’s three ToF peaks: hydrogen (\(\mathrm{H}_2^+\)), water vapor (\(\mathrm{H}_2\mathrm{O}^+\)), and nitrogen (\(\mathrm{N}_2^+\)).

| Case | N detected | \(\sigma\) no SC [mm] | \(\sigma\) with SC [mm] | Profile expansion | Particle rms \(\Delta x\) |
|---|---:|---:|---:|---:|---:|
| Injection electrons (80 MeV, H₂ target) | 100030 | 24.994 | 24.994 | ~0% | 0.082 mm |
| Extraction electrons (1.6 GeV, H₂ target) | 100011 | 9.977 | 9.977 | ~0% | 0.109 mm |
| Injection \(\mathrm{H}_2^+\) (2 u) | 99988 | 24.955 | 29.003 | **+16.22%** | 4.68 mm |
| Injection \(\mathrm{H}_2\mathrm{O}^+\) (18 u) | 99988 | 24.955 | 27.773 | **+11.30%** | 3.34 mm |
| Injection \(\mathrm{N}_2^+\) (28 u) | 99988 | 24.955 | 27.394 | **+9.77%** | 2.89 mm |

The 0.1 T guiding field suppresses electron-profile distortion (as in the PAC’09 cage design). Ions stay in the cage for microseconds and see the bunch field; lighter ions are kicked more (\(\Delta v = q\int E_\mathrm{sc}\,dt / m\)), so expansion falls from \(\mathrm{H}_2^+\) to \(\mathrm{H}_2\mathrm{O}^+\) to \(\mathrm{N}_2^+\). Virtual-IPM’s Voitkiv DDCS for **electrons** only supports H/He, so electron ionization uses a hydrogen target; ion rest masses are 2 u / 18 u / 28 u.

## Guiding-\(B\) scan (0, 50, 100, 200 G)

Scan of the cage magnetic field in **electron mode** and **ion mode** (\(\mathrm{H}_2^+\), the lightest ToF peak), at both injection (80 MeV) and extraction (1.6 GeV). Units: \(1\,\mathrm{G} = 10^{-4}\,\mathrm{T}\), so 50/100/200 G = 5/10/20 mT. Each point is space-charge on vs off, **100000** particles. Collection stays \(\approx 100\%\) over this scan (cage gap 231 mm).

```bash
./scripts/run_bscan_study.sh
python scripts/evaluate_bscan.py
```

Configs: `configs/csns_rcs_ipm/bscan/`. Summary: `output/csns_bscan_summary.csv`. Extraction ion trains use the RCS RF at 2.444 MHz (bunch spacing 409.2 ns).

### Fine e-mode scan (0–200 G, step 5 G) and 10 mm injection

Electron mode only, \(\Delta B = 5\,\mathrm{G}\) from **0 to 250 G**, plus a repeat of the residual-gas / ion scans with injection \(\sigma_x=10\,\mathrm{mm}\) (\(\sigma_y=8\,\mathrm{mm}\), same 5:4 aspect as 25×20).

Ion-mode beam-size scan (\(\sigma_x=3\)–\(20\,\mathrm{mm}\), 1 mm step) at injection and extraction, and e-mode \(B\) scans, at 100–500 kW:

```bash
./scripts/run_extended_scans.sh
python scripts/evaluate_extended.py
```

```bash
./scripts/run_fine_bscan_study.sh
python scripts/evaluate_bscan5.py
python scripts/evaluate_space_charge.py --set sig10
```

Summaries: `output/csns_bscan5_summary.csv`, `output/csns_space_charge_summary_sig10.csv`.

E-mode expansion on the 5 G grid (selected points):

| \(B\) [G] | Inj. 25×20 e− | Ext. 10×8 e− | Inj. 10×8 e− |
|---:|---:|---:|---:|
| 0 | −19.4% | +47.3% | −45.7% |
| 50 | −6.2% | −8.4% | −17.2% |
| 100 | +1.4% | +10.0% | +9.3% |
| 150 | −0.4% | −3.6% | −4.0% |
| 200 | +0.15% | +0.82% | +1.57% |
| 250 | −0.15% | −0.03% | −0.85% |

\(|\Delta|\) stays \(<1\%\) from **110 G** (painted injection), **240 G** (extraction), and **250 G** (10 mm injection). At 200–500 kW, 250 G still keeps e-mode \(\lesssim 1\%\). Ion-mode size/power scan: `output/csns_ionsize_summary.csv`.

Injection 10×8 mm at **0.1 T**:

| Case | \(\sigma\) no SC | \(\sigma\) with SC | Expansion |
|---|---:|---:|---:|
| Injection e− | 10.00 mm | 10.00 mm | ~0% |
| Injection H₂⁺ / H₂O⁺ / N₂⁺ | 9.98 mm | 18.68 / 16.91 / 16.08 mm | **+87.2 / +69.5 / +61.1%** |

H₂⁺ at 0–200 G with this beam is +97–98%. Smaller \(\sigma\) at the same bunch charge raises \(E_\mathrm{sc}\) and the relative ion expansion by about \(5\times\) versus 25×20 mm.

Space-charge profile expansion \(\sigma_\mathrm{on}/\sigma_\mathrm{off}-1\):

| \(B\) | Inj. e− | Ext. e− | Inj. \(\mathrm{H}_2^+\) | Ext. \(\mathrm{H}_2^+\) |
|---:|---:|---:|---:|---:|
| 0 G | −19.37% | **+47.30%** | +18.05% | **+31.00%** |
| 50 G | −6.21% | −8.42% | +18.05% | +31.00% |
| 100 G | +1.37% | +10.05% | +18.03% | +30.99% |
| 200 G | +0.15% | +0.82% | +17.98% | +30.93% |

Electrons: the proton bunch focuses opposite-sign secondaries when \(B=0\). Injection compresses; extraction over-kicks and the detected profile widens. By **200 G** both electron profiles are restored to \(\lesssim 1\%\) (the PAC’09 0.1 T = 1000 G design is well above this). Ions: cyclotron radii at \(\le 200\,\mathrm{G}\) are metres, so \(B\) does not suppress the ion space-charge expansion. Extraction \(\mathrm{H}_2^+\) expands more than injection (\(\sim 31\%\) vs \(\sim 18\%\)) because the bunch is shorter, smaller, and more relativistic.

## Quick start (LHC 6.5 TeV electron tracking)

This repo includes the documentation’s [electron-tracking example](https://ipmsim.gitlab.io/Virtual-IPM/examples.html#electron-tracking-complete-example), adapted for local paths and current model names (`Gaussian` field model, `InterpolatingIPM` device).

Smoke test (fast):

```bash
./scripts/run_sim.sh configs/lhc_6p5tev_electrons/smoke.xml
python scripts/analyze_output.py output/lhc_6p5tev_electrons_smoke.csv
```

Fuller run (more particles / steps):

```bash
./scripts/run_sim.sh configs/lhc_6p5tev_electrons/config.xml
```

Useful CLI flags:

```bash
./scripts/run_sim.sh configs/lhc_6p5tev_electrons/smoke.xml --dryrun
./scripts/run_sim.sh configs/lhc_6p5tev_electrons/config.xml --number-of-particles 5000
```

## Layout

| Path | Purpose |
|------|---------|
| `REPORT.md` | Brief results note |
| `configs/` | XML simulation configurations |
| `scripts/run_sim.sh` | Wrapper around `virtual-ipm` |
| `scripts/analyze_output.py` | Plot initial vs final x profiles |
| `output/` | CSV results from `BasicRecorder` |
| `plots/` | Generated figures |

## Notes

- Beam along \(z\); IPM profiles along \(x\) ([conventions](https://ipmsim.gitlab.io/Virtual-IPM/usage.html#conventions)).
- Prefer editing configs in `virtual-ipm-gui`, then run headless with `virtual-ipm`.
- Upstream source: [gitlab.com/IPMsim/Virtual-IPM](https://gitlab.com/IPMsim/Virtual-IPM)
