# AGENTS.md

## Cursor Cloud specific instructions

This repo is primarily a Python scientific-simulation project living in `IPM/`, built
around [Virtual-IPM](https://ipmsim.gitlab.io/Virtual-IPM/index.html) `2.3.1`. The repo
root also has two standalone C example files (`pseudorandom.c`, `time.c`) referenced by
the root `README.md`; they are incidental and not part of the core product.

### Environment / setup
- The Python virtualenv lives at `IPM/.venv` and is created by the update script from
  `IPM/requirements.txt`. All commands below assume it is activated:
  `source IPM/.venv/bin/activate` (or run from `IPM/` with `source .venv/bin/activate`).
- `python3-venv` (system package) is required to create the venv; it is installed at the
  system level and is not part of the update script.
- There is **no lint config, no test suite, and no CI** in this repo (no pytest,
  pre-commit, ruff/flake8, Makefile, etc.). Do not fabricate lint/test commands.

### Running the product (the "application")
The application is the `virtual-ipm` CLI plus the analysis scripts in `IPM/scripts/`.
All wrapper scripts and configs use paths relative to `IPM/`, so run them from `IPM/`.
- Fast smoke run + analysis (good end-to-end check):
  `./scripts/run_sim.sh configs/lhc_6p5tev_electrons/smoke.xml`
  then `python scripts/analyze_output.py output/lhc_6p5tev_electrons_smoke.csv`.
- `scripts/run_sim.sh` auto-discovers `virtual-ipm` from `IPM/.venv` (or a repo-root
  `.venv`), so it works even without the venv activated, as long as the venv exists.
- The heavier studies (`run_space_charge_study.sh`, `run_bscan_study.sh`,
  `run_extended_scans.sh`, `run_fine_bscan_study.sh`) run 100k-particle simulations across
  many configs and are **slow**; prefer the smoke config for quick verification. See
  `IPM/README.md` for the full study workflow and expected results.
- Outputs: CSVs land in `output/` (gitignored except committed summary CSVs), plots in
  `plots/` (gitignored except committed reference PNGs).

### Notes / gotchas
- The GUI (`virtual-ipm-gui`, installed via `pip install 'Virtual-IPM[GUI]'`) is
  desktop-only and not needed for headless runs; do not install it in cloud runs.
- `requirements.txt` pins only `Virtual-IPM==2.3.1` plus loose matplotlib/pandas/numpy;
  transitive deps (scipy, etc.) resolve automatically. Installs cleanly on Python 3.12.
