# A8.net 広告掲載URL (jpcampus.net)

Upload these UTF-8 CSV files in A8 **広告掲載URL管理 → CSV一括アップロード**.

| File | Program | URLs (approx.) |
|------|---------|----------------|
| `a8-oakhouse-placement-urls.csv` | オークハウス シェアハウス | `/stays` hub + all Oakhouse `/stay/*` |
| `a8-cross-oneroom-placement-urls.csv` | クロスワンルーム | `/stays` + all stays + housing guides |

Regenerate after stay/guide URL changes:

```bash
python3 scripts/generate_a8_placement_urls.py
```

Banner links are configured in `app/a8_affiliate.py` (override via `A8_OAKHOUSE_*` / `A8_CROSS_ONEROOM_*` env vars).
