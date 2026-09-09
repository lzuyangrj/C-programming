# IPM — Virtual-IPM simulations

CSNS RCS Ionization Profile Monitor simulations using [Virtual-IPM](https://ipmsim.gitlab.io/Virtual-IPM/index.html) 2.3.1.

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

Results at 100 kW (\(7.8\times10^{12}\) protons/bunch), ideal \(E_y\) and \(B_y=0.1\,\mathrm{T}\):

| Case | \(\sigma\) no SC [mm] | \(\sigma\) with SC [mm] | Profile expansion | Particle rms \(\Delta x\) |
|---|---:|---:|---:|---:|
| Injection electrons (80 MeV) | 24.45 | 24.45 | ~0% | 0.08 mm |
| Extraction electrons (1.6 GeV) | 9.76 | 9.76 | ~0% | 0.11 mm |
| Injection \(\mathrm{H}_2^+\) | 25.14 | 29.20 | **+16.1%** | 4.65 mm |

The 0.1 T guiding field suppresses electron-profile distortion (as in the PAC’09 cage design). Ions remain in the cage for microseconds and see several bunches, so space charge broadens the measured profile.

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
| `configs/` | XML simulation configurations |
| `scripts/run_sim.sh` | Wrapper around `virtual-ipm` |
| `scripts/analyze_output.py` | Plot initial vs final x profiles |
| `output/` | CSV results from `BasicRecorder` |
| `plots/` | Generated figures |

## Notes

- Beam along \(z\); IPM profiles along \(x\) ([conventions](https://ipmsim.gitlab.io/Virtual-IPM/usage.html#conventions)).
- Prefer editing configs in `virtual-ipm-gui`, then run headless with `virtual-ipm`.
- Upstream source: [gitlab.com/IPMsim/Virtual-IPM](https://gitlab.com/IPMsim/Virtual-IPM)
