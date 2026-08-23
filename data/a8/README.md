# A8.net 広告掲載URL (jpcampus.net)

Upload in A8 **広告掲載URL管理 → CSV一括アップロード** (UTF-8).

## CSV format (required)

| Column A | Column B |
|----------|----------|
| プログラムID | 広告掲載URL |

No header row. Example:

```text
s00000018828001,https://jpcampus.net/stays
s00000018828001,https://jpcampus.net/stay/oakhouse_994
```

## Files

| File | Program ID | Program |
|------|------------|---------|
| `a8-oakhouse-placement-urls.csv` | `s00000018828001` | オークハウス |
| `a8-cross-oneroom-placement-urls.csv` | `s00000020603002` | クロスワンルーム |

Regenerate:

```bash
python3 scripts/generate_a8_placement_urls.py
```

If Cross One Room upload fails on program ID, confirm the ID on the A8 program detail page and update `CROSS_ONEROOM_PROGRAM_ID` in the script.
