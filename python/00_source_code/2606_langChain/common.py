import yfinance as yf
from pathlib import Path
import time
import pandas as pd
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
# ▼▼▼ 定数 ▼▼▼
# 料金テーブル（USD / 1Mトークン）
PRICING = {
  # Google Gemini
  "gemini-3.1-pro":        {"input": 2.00,  "output": 12.00},
  "gemini-2.5-pro":        {"input": 1.25,  "output": 10.00},
  "gemini-2.5-flash":      {"input": 0.30,  "output": 2.50},
  "gemini-2.5-flash-lite": {"input": 0.10,  "output": 0.40},
  # OpenAI
  "gpt-5.4":               {"input": 2.50,  "output": 15.00},
  "gpt-5.4-mini":          {"input": 0.75,  "output": 4.50},
  "gpt-5.4-nano":          {"input": 0.20,  "output": 1.25},
  "gpt-4.1":               {"input": 5.00,  "output": 15.00},
  "gpt-4.1-mini":          {"input": 0.40,  "output": 1.60},
  # Anthropic Claude
  "claude-opus-4-7":       {"input": 5.00,  "output": 25.00},
  "claude-opus-4-6":       {"input": 5.00,  "output": 25.00},
  "claude-sonnet-4-6":     {"input": 3.00,  "output": 15.00},
  "claude-haiku-4-5":      {"input": 1.00,  "output": 5.00},
}
# ▼▼▼ GoogleGenerativeAI_Callback_Class ▼▼▼
class GoogleMetadataCallback(BaseCallbackHandler):
  """
  ChatGoogleGenerativeAI専用 Callback
  Ollamaの OllamaMetadataCallback と同等の出力を提供する
  usage_metadata キー:
    input_tokens  : プロンプトのトークン数
    output_tokens : 生成トークン数
    total_tokens  : 合計トークン数
  """
  def __init__(self, window: int = 5):
    self.call_count        = 0
    self.str_count         = 0
    self.total_prompt_tokens = 0
    self.total_eval_tokens   = 0
    self.elapsed_min       = 0
    self.start_time        = None
    self.all_records       = []
    self.durations         = []        # 各呼び出しの所要時間（分）
    self.window            = window
    self._call_start_time  = None      # 1回の呼び出し開始時刻
  # -------------------------------------------------------
  def on_llm_start(self, serialized, prompts, **kwargs):
    """LLM呼び出し開始時"""
    if self.call_count == 0:
      self.start_time = time.time()
    self._call_start_time = time.time()   # 今回の呼び出し開始
    # プロンプト文字数の累積
    self.str_count += len(prompts[0])
    # デバッグ確認用（必要なら有効化）
    # print(f"\n[on_llm_start #{self.call_count + 1}]")
    # print(f"prompt先頭100文字: {prompts[0][:100]}")
    # print(f"prompt文字数: {len(prompts[0])}")
  # -------------------------------------------------------
  def on_llm_end(self, response: LLMResult, **kwargs):
    """LLM呼び出し終了時"""
    self.call_count += 1
    # 今回の呼び出し所要時間（分）
    call_elapsed = (time.time() - self._call_start_time) / 60
    self.durations.append(call_elapsed)
    self.elapsed_min = (time.time() - self.start_time) / 60
    for generations in response.generations:
      for gen in generations:
        # ── usage_metadata からトークン情報を取得 ──
        usage = getattr(gen.message, "usage_metadata", {}) or {}
        self.all_records.append(usage)
        prompt_tokens = usage.get("input_tokens", 0)
        eval_tokens   = usage.get("output_tokens", 0)
        self.total_prompt_tokens += prompt_tokens
        self.total_eval_tokens   += eval_tokens
        # ── 直近 window 回の平均 ──
        recent = self.durations[-self.window:]
        avg    = sum(recent) / len(recent)
        progress = f"{self.call_count:2d}"
        print(
            f"[呼び出し #{self.call_count}] 入力: {prompt_tokens} / 出力: {eval_tokens}\n"
            f"【合計文字数】{self.str_count}"
            f"【{progress}】今回: {call_elapsed:.2f}分 "
            f"| 経過: {self.elapsed_min:.2f}分 "
            f"| 直近{len(recent)}回平均: {avg:.2f}分/回"
        )
  # -------------------------------------------------------
  def on_llm_error(self, error, **kwargs):
    """エラー発生時"""
    print(f"[ERROR] {error}")
  # -------------------------------------------------------
  def summary(self, model: str= "gemini-2.5-flash") -> dict:
    """最終サマリーを返す（任意で呼び出す）"""
    total_tokens = self.total_prompt_tokens + self.total_eval_tokens
    price = PRICING.get(model, PRICING["gemini-2.5-flash"])
    input_cost_usd  = (self.total_prompt_tokens  / 1_000_000) * price["input"]
    output_cost_usd = (self.total_eval_tokens / 1_000_000) * price["output"]
    total_cost_usd  = input_cost_usd + output_cost_usd
    usd_to_jpy = get_usd_to_jpy_yfinance()
    total_cost_jpy  = total_cost_usd * usd_to_jpy
    md = f"""
## 📊 コールバック Summary

| 項目 | 値 |
|------|-----|
| 呼び出し回数 | {self.call_count} 回 |
| 合計処理時間 | {self.elapsed_min:.2f} 分 |
| 入力トークン合計 | {self.total_prompt_tokens:,} |
| 出力トークン合計 | {self.total_eval_tokens:,} |
| 総トークン合計 | {total_tokens:,} |
| 為替レート | 1 USD = ¥{usd_to_jpy:.2f} |
| ベースモデル | {model} |
| 料金 (JPY) | ¥{total_cost_jpy:.2f} |
"""
    return md
  def meta_data(self, model: str= "gemini-2.5-flash"):
    prompt_tokens = self.total_prompt_tokens
    eval_tokens = self.total_eval_tokens
    total_tokens = self.total_prompt_tokens + self.total_eval_tokens
    price = PRICING.get(model, PRICING["gemini-2.5-flash"])
    input_cost_usd  = (prompt_tokens  / 1_000_000) * price["input"]
    output_cost_usd = (eval_tokens / 1_000_000) * price["output"]
    total_cost_usd  = input_cost_usd + output_cost_usd
    usd_to_jpy = get_usd_to_jpy_yfinance()
    total_cost_jpy  = total_cost_usd * usd_to_jpy
    return {
      "meta_data": self.all_records,
      "prompt_tokens": prompt_tokens,
      "eval_tokens": eval_tokens,
      "total_tokens": total_tokens,
      "usd_to_jpy":usd_to_jpy,
      "total_cost_jpy": total_cost_jpy
    }
# ▼▼▼ 関数　▼▼▼
def get_usd_to_jpy_yfinance() -> float:
  """
  日米為替レート取得
  """
  try:
    ticker = yf.Ticker("USDJPY=X")
    # 直近1日のデータを取得
    hist = ticker.history(period="1d")
    return round(float(hist["Close"].iloc[-1]), 2)
  except Exception as e:
    print(f"取得失敗: {e}")
    return 160.0
def res_output_md(response,dir_str=None,file_name=None):
  """
  markdownファイル出力
  """
  if (dir_str==None):
    dir_str = "out"
    dir_path = Path(f"./{dir_str}/")
    dir_path.mkdir(parents=True, exist_ok=True)
  else:
    dir_path = Path(f"./{dir_str}/")
    dir_path.mkdir(parents=True, exist_ok=True)
  if (file_name==None):
    now = datetime.now()
    formatted_time = now.strftime("%y%m%d-%H%M")
    file_name = f'test-{formatted_time}'
    with open(f"./{dir_str}/{file_name}.md", "w", encoding="utf-8") as f:
      f.write(response)
  else:
    with open(f"./{dir_str}/{file_name}.md", "w", encoding="utf-8") as f:
      f.write(response)