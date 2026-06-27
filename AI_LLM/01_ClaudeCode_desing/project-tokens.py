# ──────────────────────────
# pip install pandas
# pip install yfinance
# ──────────────────────────
import json
import os
from pathlib import Path
import pandas as pd
import yfinance as yf
# ──────────────────────────
# 定数
# ──────────────────────────
OPUS_4_8="claude-opus-4-8"
OPUS_4_7="claude-opus-4-7"
SONNET_4_6="claude-sonnet-4-6"
HAIKU_4_5="claude-haiku-4-5"
BASE_INPUT = "base-input"
CACHE_5M = "5m-cache-writes-input"
CACHE_1H = "1h-cache-writes-input"
CACHE_HITS = "cache-hits-refreshes-input"
OUTPUT =  "output"
# 料金テーブル（USD / 100万トークン）
PRICING = {
  # Anthropic Claude
  OPUS_4_8:   {BASE_INPUT: 5.00,  CACHE_5M: 6.25,  CACHE_1H: 10.00,  CACHE_HITS: 5.00,  OUTPUT: 25.00},
  OPUS_4_7:   {BASE_INPUT: 5.00,  CACHE_5M: 6.25,  CACHE_1H: 10.00,  CACHE_HITS: 5.00,  OUTPUT: 25.00},
  SONNET_4_6: {BASE_INPUT: 3.00,  CACHE_5M: 3.75,  CACHE_1H: 6.00,   CACHE_HITS: 0.30,  OUTPUT: 15.00},
  HAIKU_4_5:  {BASE_INPUT: 1.00,  CACHE_5M: 1.25,  CACHE_1H: 2.00,   CACHE_HITS: 0.10,  OUTPUT: 5.00},
}
# ──────────────────────────
# 関数
# ──────────────────────────
def find_session_dir_for_project(project_root: Path) -> Path | None:
  """
  project_root に対応する Claude Code のセッションログフォルダを探す。
  完全一致が見つからない場合は、エンコード結果の前方一致でフォールバック検索する。
  """
  projects_dir = find_claude_projects_dir()
  if not projects_dir.exists():
    return None
  encoded = encode_project_path(project_root)
  exact = projects_dir / encoded
  if exact.exists():
    return exact
  # フォールバック: 大文字小文字やドライブ文字表記揺れに対応するため前方一致で探す
  candidates = [
    d for d in projects_dir.iterdir()
    if d.is_dir() and d.name.lower().startswith(encoded.lower()[:10])
  ]
  if len(candidates) == 1:
    return candidates[0]
  return None
def find_claude_projects_dir() -> Path:
  """
  ~/.claude/projects の場所を特定する。
  CLAUDE_CONFIG_DIR が設定されていればそちらを優先する。
  """
  config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
  if config_dir:
    base = Path(config_dir)
  else:
    base = Path.home() / ".claude"
  return base / "projects"
def encode_project_path(project_path: Path) -> str:
  """
  Claude Code が ~/.claude/projects/ 配下に使うフォルダ名へのエンコード方式を再現する。
  実際にはパス中の区切り文字や記号が "-" に置換される。
  """
  raw = str(project_path.resolve())
  encoded_chars = []
  for ch in raw:
    if ch.isalnum():
      encoded_chars.append(ch)
    else:
      encoded_chars.append("-")
  return "".join(encoded_chars)
def load_jsonl_records(session_dir: Path):
  """session_dir 配下の全 .jsonl を読み込み、レコードを順次返す"""
  jsonl_files = sorted(session_dir.glob("*.jsonl"))
  for jf in jsonl_files:
    session_id = jf.stem
    with open(jf, "r", encoding="utf-8") as f:
      for line in f:
        line = line.strip()
        if not line:
          continue
        try:
          record = json.loads(line)
        except json.JSONDecodeError:
          continue
        record["_session_id"] = session_id
        record["_source_file"] = jf.name
        yield record
def extract_usage_rows(records):
  """type == 'assistant' かつ message.usage を持つレコードからトークン使用量行を抽出
     同一メッセージ(message.id)の重複行は1行に集約する"""
  rows = []
  seen_message_ids = set()
  for rec in records:
    if rec.get("type") != "assistant":
      continue
    message = rec.get("message", {})
    usage = message.get("usage")
    if not usage:
      continue
    message_id = message.get("id")
    session_id = rec.get("_session_id")
    dedupe_key = (session_id, message_id)
    # 同一メッセージIDはAPI呼び出し1回分なので、1度だけカウントする
    if message_id is not None:
      if dedupe_key in seen_message_ids:
        continue
      seen_message_ids.add(dedupe_key)
    rows.append({
      "timestamp": rec.get("timestamp"),
      "session_id": session_id,
      "source_file": rec.get("_source_file"),
      "model": message.get("model"),
      "message_id": message_id,
      "input_tokens": usage.get("input_tokens", 0) or 0,
      "output_tokens": usage.get("output_tokens", 0) or 0,
      "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0) or 0,
      "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0) or 0,
    })
  return rows
def to_tokyo_naive(series: pd.Series) -> pd.Series:
  """
  timestamp列をAsia/Tokyoのtz-naiveな文字列向け表現に変換する。
  tz-awareならUTC前提でJSTへ変換し、tz-naiveならそのまま(UTCとみなして)変換する。
  """
  ts = pd.to_datetime(series, errors="coerce")
  if ts.dt.tz is None:
    # tz情報がない場合はUTC記録と仮定してローカライズしてから変換
    ts = ts.dt.tz_localize("UTC")
  ts = ts.dt.tz_convert("Asia/Tokyo").dt.tz_localize(None)
  return ts
def calc_cost(row):
  p = PRICING.get(row["model"])
  if p is None:
    p = PRICING.get("claude-opus-4-8")
  return (
    row["input_tokens"]*p[BASE_INPUT]/1_000_000
    + row["cache_creation_input_tokens"]*p[CACHE_5M]/1_000_000
    + row["cache_read_input_tokens"]*p[CACHE_HITS]/1_000_000
    + row["output_tokens"]*p[OUTPUT]/1_000_000
  )
def get_usd_to_jpy_yfinance() -> float:
  """
  ドル円為替レート取得
  """
  try:
    ticker = yf.Ticker("USDJPY=X")
    # 直近1日のデータを取得
    hist = ticker.history(period="1d")
    return round(float(hist["Close"].iloc[-1]), 2)
  except Exception as e:
    print(f"取得失敗: {e}")
    return 160.0
def row_to_dataframe(rows):
  """dataframeに変換"""
  df = pd.DataFrame(rows)
  usd_to_jpy = get_usd_to_jpy_yfinance()
  df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
  df["timestamp"] = to_tokyo_naive(df["timestamp"])
  df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
  df = df.sort_values("timestamp")
  df.reset_index(drop=True,inplace=True)
  df2 = df[[
    "timestamp",
    "model",
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens"
    ]].copy()
  df2["total_cost"] = df2.apply(calc_cost, axis=1)
  df2["total_jp_cost"] = df2["total_cost"]*usd_to_jpy
  return df2
def export_daily_summary(df: pd.DataFrame):
  """日付ごとにtotal_costとtotal_jp_costを合算"""
  daily = df.copy()
  # timestamp(文字列 "%Y-%m-%d %H:%M:%S") から日付部分だけ抽出
  daily["date"] = daily["timestamp"].str.slice(0, 10)
  summary = (
    daily.groupby("date", as_index=False)
    .agg(
      input_tokens=("input_tokens", "sum"),
      output_tokens=("output_tokens", "sum"),
      cache_creation_input_tokens=("cache_creation_input_tokens", "sum"),
      cache_read_input_tokens=("cache_read_input_tokens", "sum"),
      total_cost=("total_cost", "sum"),
      total_jp_cost=("total_jp_cost", "sum"),
    )
    .sort_values("date")
    .reset_index(drop=True)
  )
  return summary
# ──────────────────────────
# 実行フェーズ
# ──────────────────────────
def main():
  print("プロジェクトtoken量出力します。")
  project_root = Path.cwd()
  session_dir = find_session_dir_for_project(project_root)
  if session_dir is None:
    print("セッションログが見つかりませんでした。")
    return
  records = load_jsonl_records(session_dir)
  rows = extract_usage_rows(records)
  df_data = row_to_dataframe(rows)
  df_summary = export_daily_summary(df_data)
  detail_path = project_root  / "zz_dev/claude_token_data.tsv"
  daily_path = project_root / "zz_dev/claude_token_daily_summary.tsv"
  detail_path.parent.mkdir(parents=True, exist_ok=True)
  daily_path.parent.mkdir(parents=True, exist_ok=True)
  df_data.to_csv(detail_path, index=False, encoding="utf-8", sep="\t")
  df_summary.to_csv(daily_path, index=False, encoding="utf-8", sep="\t")
  print("プロジェクトtoken量出力完了しました。")
if __name__ == "__main__":
  main()