import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
import pandas as pd
import my_func
# ファイル読み込み
input_path = Path('./osv-result.json')
with open(input_path, encoding="utf-8") as f:
  data = json.load(f)
#df = my_func.parse_osv_json(data)
df = my_func.parse_osv_json(data, min_severity="HIGH", pl="python")
df.to_csv("result.csv", index=True,sep="\t", encoding="utf-8-sig")