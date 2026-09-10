# E-mode parameter-scan replan

XML files in this directory are generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --emode-replan
./scripts/run_emode_replan.sh --matrix   # show the matrix, run nothing
./scripts/run_emode_replan.sh            # run the missing points
```

## Why replan

The previous e-mode campaign used a **0–250 G / 5 G** grid for painted injection (25×20 mm) and extraction (10×8 mm) at 100–500 kW, and for 10 mm injection (10×8 mm) at 100 kW only. It resolved the oscillatory recovery vs \(B\), but:

- it stopped at 250 G, where extraction at 500 kW is still +0.88% and 10 mm injection is −0.85% — no margin shown;
- the **10 mm injection** family (most \(B\)-hungry case) was never run at 200–500 kW;
- **beam size**, **cage voltage**, and **beam offset** were never scanned in e-mode.

## Beam shape

**All blocks use round beams, \(\sigma_y = \sigma_x\)** (25×25 mm painted injection, 10×10 mm extraction and small injection, \(\sigma\times\sigma\) in the size scan). The earlier elliptical runs (\(\sigma_y = 0.8\,\sigma_x\)) are kept as the closed reference in sections 1–6 of `REPORT.md` but are **not reused** here; every point of this plan is a new run.

## Matrix

Common settings: 100000 secondaries, Voitkiv DDCS on hydrogen, SC on vs off (SC-off runs only at 100 kW — they do not depend on \(N_b\) and are shared), \(N_b\propto P\), uniform \(E_y = V/231\,\mathrm{mm}\) (25 kV → 108 kV/m unless scanned).

| Block | Beams | \(\sigma_x = \sigma_y\) | \(B\) | Power | SC runs |
|---|---|---|---|---|---|
| **A** \(B\)-scan | inj. 80 MeV; ext. 1.6 GeV; inj. 80 MeV | 25 mm; 10 mm; 10 mm | **0–300 G, step 5 G** (61 values) | 100–500 kW | on ×5 powers + off ×1 |
| **B** size scan | inj. 80 MeV; ext. 1.6 GeV | **3–20 mm, step 1 mm** | 0, 100, 200, 300 G, and 0.1 T (1000 G) | 100–500 kW | on ×5 + off ×1 |
| **C** cage voltage | inj. 80 MeV | 10 mm | 0–300 G step 25 G, and 0.1 T | 100, 500 kW | on ×2 + off ×1 |
| **D** beam offset | inj. 80 MeV; ext. 1.6 GeV | 10 mm | 0, 100, 200, 300 G, 0.1 T | 100, 500 kW | on ×2 + off ×1 |

Block C voltages: **5, 10, 15, 20, 25, 30 kV** (step 5 kV; \(E_y\) = 22, 43, 65, 87, 108, 130 kV/m). Block D offsets \((\Delta x, \Delta y)\): **(+5, 0), (+10, 0), (0, +5), (0, −5) mm** via `TransverseOffset` of the bunch train; \(+y\) is away from the electron detector (detector at \(y_\min\)). Centred baselines for C (25 kV) and D come from Block A (10×10 mm injection / extraction).

Points shared by A and B (10 mm at 0/100/200/300 G) are counted once.

Run counts (`--matrix`):

| Block / family | runs | done | to run |
|---|---:|---:|---:|
| A B-scan inj. e− 25×25 mm, 100–500 kW | 366 | 0 | 366 |
| A B-scan ext. e− 10×10 mm, 100–500 kW | 366 | 0 | 366 |
| A B-scan inj. e− 10×10 mm, 100–500 kW | 366 | 0 | 366 |
| B size scan inj. e− 3–20 mm (new points) | 516 | 0 | 516 |
| B size scan ext. e− 3–20 mm (new points) | 516 | 0 | 516 |
| C cage voltage 5–30 kV, inj. e− 10×10 mm | 252 | 0 | 252 |
| D beam offset inj. e− 10×10 mm, 4 offsets | 60 | 0 | 60 |
| D beam offset ext. e− 10×10 mm, 4 offsets | 60 | 0 | 60 |
| **Total** | **2502** | **0** | **2502** |

**Status: planned, not executed.** Estimated cost: ~1 min per run, ~10.5 h wall time at `JOBS=4`, ~27 MB per CSV (~68 GB).

File naming in `output/emode/`: A/B `csns_{beam}_electrons_s{σ}x{σ}mm_p{P}kw_b{B}G_sc_{on,off}.csv`; C `..._s10x10mm_v{V}kv_p{P}kw_...`; D `..._s10x10mm_dx{dx}mm_dy{dy}mm_p{P}kw_...` (negative offsets written as `m5`).

Outputs: `output/csns_emode_{bscan300,size,voltage,offset}_summary.csv`; `plots/csns_emode_bscan300.png`, `csns_emode_bscan300_tail.png`, `csns_emode_size_expansion.png`, `csns_emode_size_obtained.png`, `csns_emode_voltage.png`, `csns_emode_offset.png`.
