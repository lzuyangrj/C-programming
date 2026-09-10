# E-mode parameter-scan replan

XML files in this directory are generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --emode-replan
./scripts/run_emode_replan.sh
```

## Why replan

The previous e-mode campaign used a **0–250 G / 5 G** grid. That resolved the oscillatory recovery vs \(B\) (keep those runs as the high-resolution \(B\) reference) but:

- oversampled \(B\) where the curve is already flat (painted injection recovers by ~110 G);
- scanned power only for painted injection (25×20 mm) and extraction (10×8 mm);
- never scanned **beam size** in e-mode (ion-mode did 3–20 mm);
- never scanned the **10 mm injection** family at 200–500 kW — the most \(B\)-hungry e-mode case at 100 kW.

## New matrix (this directory)

Closed — do **not** re-run: fine 5 G \(B\) scans at 100–500 kW for painted injection and extraction.

| Scan | \(\sigma_x\) | \(B\) | Power | Stage | Space charge |
|---|---|---|---|---|---|
| Size × diagnostic \(B\) × \(P\) | 3–20 mm, 1 mm; \(\sigma_y=0.8\sigma_x\) | 0, 250 G, 0.1 T (1000 G) | 100–500 kW | injection + extraction | on; off reused from 100 kW |
| 10 mm injection \(B\times P\) fill-in | 10×8 mm | 50, 100, 150, 200 G (0 / 250 G / 0.1 T already in the size scan; 100 kW already in the 5 G scan) | 200–500 kW | injection | on; off from the 100 kW 5 G scan |

Diagnostic \(B\) values: **0** (worst space-charge kick), **250 G** (previous \(\lesssim 1\%\) edge), **0.1 T** (PAC’09 design). Particle count stays **100000**. Voitkiv DDCS on hydrogen.

Existing matching CSVs (10 mm at 100 kW, extraction 10 mm at high \(P\) for \(B=0\) and 250 G) are hard-linked into `output/emode/` and skipped.
