# Virtual-IPM project

Working setup for [Virtual-IPM](https://ipmsim.gitlab.io/Virtual-IPM/index.html) (v2.3.1), a modular simulator for electron/ion transport in Ionization Profile Monitors (IPM) and related devices (e.g. BIF).

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
