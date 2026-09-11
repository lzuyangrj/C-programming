# Ion-mode parameter-scan matrix

Parallel to the e-mode replan (`../emode/README.md`). XML files here are
generated (not stored in git):

```bash
python3 scripts/generate_csns_configs.py --imode-matrix   # counts only
python3 scripts/generate_csns_configs.py --imode-replan   # write XMLs
./scripts/run_imode_replan.sh --matrix
JOBS=4 ./scripts/run_imode_replan.sh
```

## Why a separate ion matrix

The closed ion campaigns (elliptical beams) covered:

- design \(B_y=0.1\,\mathrm{T}\) residual-gas profiles (H₂⁺, H₂O⁺, N₂⁺);
- coarse B 0/50/100/200/250 G for H₂⁺ (expansion **flat** in B);
- size × power at **0.1 T only** (elliptical \(\sigma_y=0.8\sigma_x\)).

They never scanned **cage voltage** or **beam offset** in ion mode, never used
**round beams** to match the e-mode replan, and never combined size with more
than the design field. The useful e-mode axes for ions are **size, voltage
(ToF), and offset** — not a B-scan.

## Beam shape, species, and \(B\)

**Round beams, \(\sigma_y=\sigma_x\)** (25×25 mm painted injection, 10×10 mm
extraction and small injection, \(\sigma\times\sigma\) in the size scan). The
elliptical ionsize / bscan CSVs are **not** reused.

Species = the three ToF peaks: **H₂⁺**, **H₂O⁺**, **N₂⁺**. SC-off trajectories
have no bunch field, so obtained \(x\) = birth \(x\) independent of mass: only
**H₂⁺ SC-off at 100 kW** is written and shared across species and powers.

**\(B_y\in\{0,200,1000\}\,\mathrm{G}\)** in every block (no guide / mid
checkpoint / design 0.1 T). No ion B-scan grid — closed H₂⁺ scans are flat
vs \(B\) at ≤250 G (cyclotron radii are metres).

## Matrix (Blocks A–D)

Common settings: 100000 secondaries, ion rest mass 2/18/28 u, circular 3-bunch
train, sim 12 µs / 8000 steps, Boris, RNG 1234, \(N_b\propto P\), cage
\(E_y = -V/231\,\mathrm{mm}\) (ions collected at \(y_\min\); sign flipped vs
e-mode). Design \(V=25\,\mathrm{kV}\) unless Block C scans it.

| Block | Beams | \(\sigma_x=\sigma_y\) | \(B\) | Power | Species |
|---|---|---|---|---|---|
| **A** ref. beams | inj.; ext.; inj. | 25 / 10 / 10 mm | **0, 200, 1000 G** | 100–500 kW | 3 |
| **B** size scan | inj.; ext. | **3–20 mm, step 1 mm** | 0, 200, 1000 G | 100–500 kW | 3 |
| **C** cage voltage | inj. | 10 mm | 0, 200, 1000 G | 100, 500 kW | 3 |
| **D** beam offset | inj.; ext. | 10 mm | 0, 200, 1000 G | 100, 500 kW | 3 |

Block C voltages: **5, 10, 15, 20, 25, 30 kV**. Block D offsets
\((\Delta x,\Delta y)\): **(+5, 0), (+10, 0), (0, +5), (0, −5) mm**; \(+y\) is
away from the detector at \(y_\min\). Centred / 25 kV baselines come from
Block A.

### Run counts (`--imode-matrix`)

Per geometry: SC-on × 3 species × powers, plus one H₂⁺ SC-off at 100 kW
→ **16 files** per (beam, σ, B) in A/B; **7 files** per (V or offset, B) in
C/D (3 spp × 2 powers SC-on + 1 H₂⁺ SC-off).

| Block / family | formula | runs |
|---|---|---:|
| A ref. beams (3 × 3 B × 16) | \(3\times 3\times 16\) | 144 |
| B size scan full product | \(2\times 18\times 3\times 16\) | 1728 |
| A∩B (10×10 mm at all three B, in A) | \(2\times 3\times 16\) | 96 |
| B new | 1728 − 96 | 1632 |
| C cage voltage | \(6\times 3\times 7\) | 126 |
| D beam offset | \(2\times 4\times 3\times 7\) | 168 |
| **Grand (A + B-new + C + D)** | | **2070** |

Print live done/to-run counts with `--imode-matrix`. **Status: complete**
(2070 / 2070). Results: `REPORT.md` §10; evaluate with
`python3 scripts/evaluate_imode.py`.

### vs e-mode

| | E-mode replan | Ion-mode matrix |
|---|---|---|
| Beams | round \(\sigma_y=\sigma_x\) | same |
| \(B\) | dense grids (5 G / 25 G / checkpoints) | **0, 200, 1000 G only** |
| Block B size | 3–20 mm | same × **3 species** |
| Block C \(V\) | 5–30 kV / 5 kV | same × 3 species |
| Block D offset | 4 offsets | same × 3 species |
| Secondaries | electrons (Voitkiv H₂) | H₂⁺ / H₂O⁺ / N₂⁺ |
| Total runs | 2502 | **2070** |

### Not in this plan

- Any ion B-scan denser than {0, 200, 1000} G
- Elliptical beams (closed in REPORT §§1–6)
- Fine C/D densification (wait for coarse ion C/D)
- Bunch-length / mid-ramp energy / MCP / non-uniform cage

File naming in `output/imode/`:
`csns_{beam}_{ions|h2o_ions|n2_ions}_s{σ}x{σ}mm_p{P}kw_b{B}G_sc_{on,off}.csv`
(voltage / offset tags as in e-mode: `_v{V}kv_`, `_dx…_dy…_`).
