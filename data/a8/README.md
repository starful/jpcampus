# A8.net 広告掲載URL (jpcampus.net)

**プログラム単位管理:** [`/opt/work/data/a8/`](../../../data/a8/README.md)

| プログラム | ID | CSV |
|------------|-----|-----|
| オークハウス | `s00000018828001` | `s00000018828001.csv` |
| クロスワンルーム | `s00000020603002` | `s00000020603002.csv` |

```bash
python3 /opt/work/data/a8/generate_placement_urls.py -p oakhouse
python3 /opt/work/data/a8/generate_placement_urls.py -p cross_oneroom
```

## CSV format

| Column A | Column B |
|----------|----------|
| プログラムID | 広告掲載URL |

No header · UTF-8
