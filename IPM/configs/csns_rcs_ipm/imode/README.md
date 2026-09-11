# Ion-mode parameter-scan matrix

Parallel to the e-mode replan (`../emode/README.md`). XML files here are
generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --imode-matrix   # counts only
python scripts/generate_csns_configs.py --imode-replan   # write XMLs
./scripts/run_imode_replan.sh --matrix
JOBS=4 ./scripts/run_imode_replan.sh
```

## Why a separate ion matrix

The closed ion campaigns (elliptical beams) covered:

- design \(B_y=0.1\,\mathrm{T}\) residual-gas profiles (H₂⁺, H₂O⁺, N₂⁺);
- coarse B 0/50/100/200/250 G for H₂⁺ (expansion flat in B);
- size × power at **0.1 T only** (elliptical \(\sigma_y=0.8\sigma_x\)).

They never scanned **cage voltage** or **beam offset** in ion mode, never used
**round beams** to match the e-mode replan, and never combined size with a
B-checkpoint grid. The e-mode A–D axes (B, size, V, offset) are the right
map; ion physics changes the **B densification**.

## Beam shape and species

**Round beams, \(\sigma_y=\sigma_x\)** (25×25 mm painted injection, 10×10 mm
extraction and small injection, \(\sigma\times\sigma\) in the size scan). The
elliptical ionsize / bscan CSVs are **not** reused.

Species = the three ToF peaks: **H₂⁺**, **H₂O⁺**, **N₂⁺**. SC-off trajectories
have no bunch field, so obtained \(x\) = birth \(x\) independent of mass: only
**H₂⁺ SC-off at 100 kW** is written and shared across species and powers.

## Matrix (Blocks A–D)

Common settings: 100000 secondaries, ion rest mass 2/18/28 u, circular 3-bunch
train, sim 12 µs / 8000 steps, Boris, RNG 1234, \(N_b\propto P\), cage
\(E_y = -V/231\,\mathrm{mm}\) (ions collected at \(y_\min\); sign flipped vs
e-mode). Design \(V=25\,\mathrm{kV}\) unless Block C scans it.

| Block | Beams | \(\sigma_x=\sigma_y\) | \(B\) | Power | Species |
|---|---|---|---|---|---|
| **A** \(B\)-scan | inj.; ext.; inj. | 25 / 10 / 10 mm | **0, 50, 100, 200, 300, 1000 G** (sparse) | 100–500 kW | 3 |
| **B** size scan | inj.; ext. | **3–20 mm, step 1 mm** | 0, 100, 200, 300 G, 0.1 T | 100–500 kW | 3 |
| **C** cage voltage | inj. | 10 mm | 0–300 G step 25 G, and 0.1 T | 100, 500 kW | 3 |
| **D** beam offset | inj.; ext. | 10 mm | 0, 100, 200, 300 G, 0.1 T | 100, 500 kW | 3 |

Block C voltages: **5, 10, 15, 20, 25, 30 kV**. Block D offsets
\((\Delta x,\Delta y)\): **(+5, 0), (+10, 0), (0, +5), (0, −5) mm**; \(+y\) is
away from the detector at \(y_\min\). Centred / 25 kV baselines come from
Block A.

### Why B is sparse in A (unlike e-mode)

E-mode needed 0–300 G / 5 G because electron recovery **oscillates** with \(B\).
Ion-mode expansion at ≤250 G is **flat** (cyclotron radii are metres); the
closed H₂⁺ B-scan and the 10 mm injection repeat both show that. Block A only
needs enough checkpoints to confirm flatness through 300 G and the 0.1 T
design field. Size, voltage (ToF / dwell time), and offset carry more
information for ions.

### Run counts (`--imode-matrix`)

Per geometry: SC-on × 3 species × powers, plus one H₂⁺ SC-off at 100 kW
→ **16 files** per (beam, σ, B) in A/B; **7 files** per (V or offset, B) in
C/D (3 spp × 2 powers SC-on + 1 H₂⁺ SC-off).

| Block / family | formula | runs |
|---|---|---:|
| A B-scan (3 ref. beams × 6 B × 16) | \(3\times 6\times 16\) | 288 |
| B size scan full product | \(2\times 18\times 5\times 16\) | 2880 |
| A∩B (10×10 mm at size-scan B, in A) | \(2\times 5\times 16\) | 160 |
| B new | 2880 − 160 | 2720 |
| C cage voltage | \(6\times 14\times 7\) | 588 |
| D beam offset | \(2\times 4\times 5\times 7\) | 280 |
| **Grand (A + B-new + C + D)** | | **3876** |

Print live done/to-run counts with `--imode-matrix`. **Status: planned, not
executed.**

### vs e-mode

| | E-mode replan | Ion-mode matrix |
|---|---|---|
| Beams | round \(\sigma_y=\sigma_x\) | same |
| Block A \(B\) | 0–300 G / **5 G** (61) | **0/50/100/200/300/1000 G** (6) |
| Block B size | 3–20 mm at 5 checkpoint \(B\) | same grid × **3 species** |
| Block C \(V\) | 5–30 kV / 5 kV, 14 \(B\) | same × 3 species |
| Block D offset | 4 offsets, 5 \(B\) | same × 3 species |
| Secondaries | electrons (Voitkiv H₂) | H₂⁺ / H₂O⁺ / N₂⁺ |
| Total runs | 2502 | **3876** |

### Not in this plan

- Dense 5 G ion B-scan (rejected: flat)
- Elliptical beams (closed in REPORT §§1–6)
- Fine C/D densification (wait for coarse ion C/D)
- Bunch-length / mid-ramp energy / MCP / non-uniform cage

File naming in `output/imode/`:
`csns_{beam}_{ions|h2o_ions|n2_ions}_s{σ}x{σ}mm_p{P}kw_b{B}G_sc_{on,off}.csv`
(voltage / offset tags as in e-mode: `_v{V}kv_`, `_dx…_dy…_`).
