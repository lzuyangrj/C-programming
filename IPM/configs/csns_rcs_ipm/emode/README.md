# E-mode parameter-scan replan

XML files in this directory are generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --emode-replan
./scripts/run_emode_replan.sh --matrix   # show the matrix, run nothing
./scripts/run_emode_replan.sh            # run the missing points
```

## Why replan

The previous e-mode campaign used a **0–250 G / 5 G** grid for painted injection (25×20 mm) and extraction (10×8 mm) at 100–500 kW, and for 10 mm injection at 100 kW only. It resolved the oscillatory recovery vs \(B\), but:

- it stopped at 250 G, where extraction at 500 kW is still +0.88% and 10 mm injection is −0.85% — no margin shown;
- the **10 mm injection** family (most \(B\)-hungry case) was never run at 200–500 kW;
- **beam size** was never scanned in e-mode (ion-mode had 3–20 mm).

## Matrix

Common settings: 100000 secondaries, Voitkiv DDCS on hydrogen, SC on vs off (SC-off runs only at 100 kW — they do not depend on \(N_b\) and are shared), \(N_b\propto P\), \(\sigma_y=0.8\,\sigma_x\), uniform \(E_y\approx108\,\mathrm{kV/m}\).

| Block | Beams | \(\sigma_x\) | \(B\) | Power | SC runs |
|---|---|---|---|---|---|
| **A** \(B\)-scan | inj. 80 MeV; ext. 1.6 GeV; inj. 80 MeV | 25 mm (painted); 10 mm; 10 mm | **0–300 G, step 5 G** (61 values) | 100–500 kW | on ×5 powers + off ×1 |
| **B** size scan | inj. 80 MeV; ext. 1.6 GeV | **3–20 mm, step 1 mm** | 0, 100, 200, 300 G, and 0.1 T (1000 G) | 100–500 kW | on ×5 + off ×1 |

Points shared by A and B (10 mm at 0/100/200/300 G) are counted once. Existing CSVs with identical parameters (the 0–250 G scans, the 0.1 T design runs) are hard-linked into `output/emode/` and skipped.

Run counts at the time of planning (`--matrix`):

| Block / family | runs | done | to run |
|---|---:|---:|---:|
| A B-scan inj. e− σx = 25 mm, 100–500 kW | 366 | 306 | 60 |
| A B-scan ext. e− σx = 10 mm, 100–500 kW | 366 | 306 | 60 |
| A B-scan inj. e− σx = 10 mm, 100–500 kW | 366 | 102 | 264 |
| B size scan inj. e− 3–20 mm (new points) | 516 | 2 | 514 |
| B size scan ext. e− 3–20 mm (new points) | 516 | 17 | 499 |
| **Total** | **2130** | **733** | **1397** |

File naming: `csns_{beam}_electrons_s{σx}mm_p{P}kw_b{B}G_sc_{on,off}.csv` in `output/emode/`.

Outputs: `output/csns_emode_bscan300_summary.csv`, `output/csns_emode_size_summary.csv`, `plots/csns_emode_bscan300.png`, `plots/csns_emode_bscan300_tail.png`, `plots/csns_emode_size_expansion.png`, `plots/csns_emode_size_obtained.png`.
