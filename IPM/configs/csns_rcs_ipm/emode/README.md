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

**Status: complete** (2502 / 2502). Results: `REPORT.md` §8.

## Fine C/D (running)

Coarse C/D undersample the region that actually moves: the 10–15 kV sign flip at \(B=0\), the 0–150 G oscillations (25 G is too coarse; Block A used 5 G only at 25 kV), and \(\Delta y\). \(\Delta x\) is translation-invariant for a Gaussian bunch in a uniform cage. Write-up: `REPORT.md` §9.

```bash
python scripts/generate_csns_configs.py --emode-fine-cd-matrix
./scripts/run_emode_fine_cd.sh --matrix
JOBS=4 ./scripts/run_emode_fine_cd.sh
```

This is **not** part of `--emode-replan` / `run_emode_replan.sh`. SKIP if the CSV exists.

Held fixed: 100000 e−, Voitkiv H₂, round 10×10 mm, SC-off at 100 kW shared, \(P=100,500\,\mathrm{kW}\). Reuse coarse C (252), coarse D (120), Block A 25 kV / 5 G, and Block A centred \(\Delta y=0\).

| Slice | Grid | New runs |
|---|---|---:|
| **C1** | \(V=5\)–30 kV / **1 kV** (26) × diagnostic \(B\) (0, 25, 50, 75, 100, 125, 150, 200, 250, 300, 1000 G) | 660 |
| **C2** | \(V=10,12,15,18,20\,\mathrm{kV}\) × \(B=0\)–300 G / **5 G** + 0.1 T. 25 kV / 5 G = Block A | 738 |
| **C union** | not the full 1 kV × 5 G cartesian (that would be 4584 new) | **1398** |
| **D1** | \(\Delta y=-10\ldots+10\,\mathrm{mm}\) / **1 mm**, \(\Delta x=0\); same diagnostic \(B\); inj.+ext. \(\Delta y=0\) = Block A | 1260 |
| **D2** | \(\Delta y=\pm 5\,\mathrm{mm}\) × 5 G \(B\)-scan; inj.+ext. **No \(\Delta x\) scan** | 612 |
| **D union** | | **1872** |
| **C+D fine** | | **3270** |

Execution order when requested: C1, C2, D1, D2. SKIP if CSV exists. Evaluator overlays Block A for 25 kV / 5 G and for \(\Delta y=0\).

## Detailed matrix

Held fixed in every run unless a block scans that axis.

| Quantity | Value |
|---|---|
| Mode | electrons only (Voitkiv DDCS, `GasType` Hydrogen) |
| Particles | 100000 |
| Tracker | Boris, 8000 steps |
| Cage | 220 mm × 231 mm, detector at \(y_\min\) |
| \(E_y\) (A, B, D) | \(25\,\mathrm{kV}/231\,\mathrm{mm} = 1.082251\times10^5\,\mathrm{V/m}\) |
| Beam | protons, \(Z=1\); **round** \(\sigma_y=\sigma_x\) |
| Injection | 80 MeV, \(\sigma_t=120\,\mathrm{ns}\), sim 1100 ns |
| Extraction | 1.6 GeV, \(\sigma_t=20\,\mathrm{ns}\), sim 220 ns |
| Bunch train | `SingleBunch` |
| Space charge | Gaussian bunch \(E\) + Lorentz-boosted bunch \(B\); off = those fields off |
| SC-off | once per geometry at 100 kW, reused at other powers (\(N_b\) does not enter the trajectory) |
| RNG | 1234 |

Bunch population \(N_b = 7.80\times10^{12}\times(P/100\,\mathrm{kW})\):

| \(P\) [kW] | 100 | 200 | 300 | 400 | 500 |
|---|---:|---:|---:|---:|---:|
| \(N_b\) | \(7.80\times10^{12}\) | \(1.56\times10^{13}\) | \(2.34\times10^{13}\) | \(3.12\times10^{13}\) | \(3.90\times10^{13}\) |

### Block A — \(B\) scan

Cartesian product, one family at a time.

| Axis | Values | \(n\) |
|---|---|---:|
| Family | inj. 80 MeV 25×25 mm; ext. 1.6 GeV 10×10 mm; inj. 80 MeV 10×10 mm | 3 |
| \(B_y\) | 0, 5, 10, …, 300 G (\(B_y = B[\mathrm{G}]\times10^{-4}\,\mathrm{T}\)) | 61 |
| \(P\) | 100, 200, 300, 400, 500 kW | 5 |
| SC | on at every \(P\); off at 100 kW only | 6 / family / \(B\) |

Runs: \(3\times 61\times 6 = 1098\). Per family: \(61\times 6 = 366\).

### Block B — size scan

| Axis | Values | \(n\) |
|---|---|---:|
| Stage | inj. 80 MeV; ext. 1.6 GeV | 2 |
| \(\sigma_x=\sigma_y\) | 3, 4, 5, …, 20 mm | 18 |
| \(B_y\) | 0, 100, 200, 300 G, and 0.1 T (1000 G) | 5 |
| \(P\) | 100, 200, 300, 400, 500 kW | 5 |
| SC | on ×5 + off ×1 | 6 / stage / \(\sigma\) / \(B\) |

Full product: \(2\times 18\times 5\times 6 = 1080\).

**Overlap with A** (counted once in the total): the two 10×10 mm families at \(B\in\{0,100,200,300\}\,\mathrm{G}\) (not 1000 G — that field is Block B only). \(2\times 4\times 6 = 48\).

New Block B points: \(1080-48=1032\) (516 per stage).

### Block C — cage voltage (inj. 10×10 mm)

| Axis | Values | \(n\) |
|---|---|---:|
| Stage / size | inj. 80 MeV, 10×10 mm | 1 |
| Cage \(V\) | 5, 10, 15, 20, 25, 30 kV | 6 |
| \(E_y=V/231\,\mathrm{mm}\) | 21.6, 43.3, 64.9, 86.6, 108.2, 129.9 kV/m | 6 |
| \(B_y\) | 0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300 G, and 0.1 T | 14 |
| \(P\) | 100, 500 kW | 2 |
| SC | on ×2 + off ×1 | 3 / \(V\) / \(B\) |

Runs: \(6\times 14\times 3 = 252\). The 25 kV / 10×10 mm / injection family of Block A is the same beam and voltage as C at \(B\in\{0,25,\ldots,300\}\,\mathrm{G}\), but C still writes its own `s10x10mm_v25kv` files so the voltage block is self-contained (evaluator does not mix A and C filenames).

### Block D — beam offset (10×10 mm)

| Axis | Values | \(n\) |
|---|---|---:|
| Stage | inj. 80 MeV; ext. 1.6 GeV | 2 |
| Size | 10×10 mm | 1 |
| \((\Delta x,\Delta y)\) | (+5, 0), (+10, 0), (0, +5), (0, −5) mm | 4 |
| \(B_y\) | 0, 100, 200, 300 G, 0.1 T | 5 |
| \(P\) | 100, 500 kW | 2 |
| SC | on ×2 + off ×1 | 3 / stage / offset / \(B\) |
| Cage \(V\) | 25 kV | 1 |

Runs: \(2\times 4\times 5\times 3 = 120\) (60 per stage). \(+y\) is away from the detector. Centred \((\Delta x,\Delta y)=(0,0)\) is Block A at the same \(B\) and \(P\), not repeated.

`TransverseOffset` is in millimetres in the XML; a 2000-particle smoke test of (+10, 0) mm put the detected centroid at \(x=+10.0\,\mathrm{mm}\).

### Totals

| | A | B new | A∩B (in A, not double-counted) | C | D | **Grand** |
|---|---:|---:|---:|---:|---:|---:|
| SC on | 915 | 860 | 40 | 168 | 80 | **2023** |
| SC off | 183 | 172 | 8 | 84 | 40 | **479** |
| All | 1098 | 1032 | 48 | 252 | 120 | **2502** |

Grand total = A + B-new + C + D = \(1098+1032+252+120=2502\) (A∩B is already inside A).

### Not in this plan

- Dense ion \(B\) grids (see the separate ion-mode matrix under `imode/`)
- Elliptical beams (\(\sigma_y=0.8\sigma_x\)); those remain the closed §1–6 results
- Bunch-length \(\sigma_t\) scan; mid-ramp energy
- Circular bunch train / second-bunch check
- Gas species (Voitkiv H/He only)
- MCP / non-uniform cage fields

File naming in `output/emode/`: A/B `csns_{beam}_electrons_s{σ}x{σ}mm_p{P}kw_b{B}G_sc_{on,off}.csv`; C `..._s10x10mm_v{V}kv_p{P}kw_...`; D `..._s10x10mm_dx{dx}mm_dy{dy}mm_p{P}kw_...` (negative offsets written as `m5`).

Outputs: `output/csns_emode_{bscan300,size,voltage,offset}_summary.csv`; `plots/csns_emode_bscan300.png`, `csns_emode_bscan300_tail.png`, `csns_emode_size_expansion.png`, `csns_emode_size_obtained.png`, `csns_emode_voltage.png`, `csns_emode_offset.png`.
