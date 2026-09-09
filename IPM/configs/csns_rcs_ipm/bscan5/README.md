# Fine e-mode \(B\) scan

XML files in this directory are generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --fine-bscan
```

41 field values (0–200 G, step 5 G) × {injection 25×20 mm, extraction 10×8 mm, injection 10×8 mm} × {SC on, SC off} = 246 configs. See `scripts/run_fine_bscan_study.sh`.
