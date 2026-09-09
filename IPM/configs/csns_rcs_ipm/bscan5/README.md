# Fine e-mode \(B\) scan

XML files in this directory are generated (not stored in git):

```bash
python scripts/generate_csns_configs.py --fine-bscan
```

51 field values (0–250 G, step 5 G) × {injection 25×20 mm, extraction 10×8 mm, injection 10×8 mm} × {SC on, SC off} = 306 configs. Power and ion-size scans: `python scripts/generate_csns_configs.py --fine-bscan --extended` and `scripts/run_extended_scans.sh`.
