import yfinance as yf
from pathlib import Path
import tiktoken
import time
import pandas as pd
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter
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
# ▼▼▼ Ollam_Callback_Class ▼▼▼
class OllamaMetadataCallback(BaseCallbackHandler):
  """
  Ollama専用callback
  """
  def __init__(self, window=5):
    self.call_count = 0
    self.str_count = 0
    self.total_prompt_tokens = 0
    self.total_eval_tokens = 0
    self.elapsed_min = 0
    self.start_time = None
    self.all_records = []
    self.durations = []
    self.window = window
  def on_llm_start(self, serialized, prompts, **kwargs):
    if self.call_count == 0:
      self.start_time = time.time()
    #確認
    #print(f"\n[on_llm_start #{self.call_count + 1}]")
    #print(f"prompt先頭100文字: {prompts[0][:100]}")
    #print(f"prompt文字数: {len(prompts[0])}")
    self.str_count += len(prompts[0])
  def on_llm_end(self, response, **kwargs):
    self.call_count += 1
    for generations in response.generations:
      for gen in generations:
        ## meta情報
        meta = gen.message.response_metadata
        self.all_records.append(meta)
        ## トークン情報
        prompt_tokens = meta.get("prompt_eval_count", 0)
        eval_tokens   = meta.get("eval_count", 0)
        self.total_prompt_tokens += prompt_tokens
        self.total_eval_tokens   += eval_tokens
        ## 処理時間
        duration_min = meta.get("total_duration", 0) / 1_000_000_000 / 60
        self.durations.append(duration_min)
        self.elapsed_min = (time.time() - self.start_time) / 60
        recent = self.durations[-self.window:]
        avg = sum(recent) / len(recent)
        progress   = f"{self.call_count:2d}"
        print(
          f"[呼び出し #{self.call_count}] 入力: {prompt_tokens} / 出力: {eval_tokens}\n"
          f"【合計文字数】{self.str_count}"
          f"【{progress}】今回: {duration_min:.2f}分 |経過: {self.elapsed_min:.2f}分 | 直近{len(recent)}回平均: {avg:.2f}分/回"
        )
  def summary(self):
    total = self.total_prompt_tokens + self.total_eval_tokens
    print("【📊 トークン集計】")
    print(f"呼び出し回数    : {self.call_count}")
    print(f"合計処理時間    : {self.elapsed_min:.2f}分")
    print(f"入力トークン合計: {self.total_prompt_tokens:,}")
    print(f"出力トークン合計: {self.total_eval_tokens:,}")
    print(f"総トークン合計  : {total:,}")
    print("="*40)
  def meta_data(self):
    prompt_tokens = self.total_prompt_tokens
    eval_tokens = self.total_eval_tokens
    total_tokens = self.total_prompt_tokens + self.total_eval_tokens
    return {
      "meta_data": self.all_records,
      "prompt_tokens": prompt_tokens,
      "eval_tokens": eval_tokens,
      "total_tokens": total_tokens
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
  def summary(self) -> dict:
    """最終サマリーを返す（任意で呼び出す）"""
    total_tokens = self.total_prompt_tokens + self.total_eval_tokens
    # summary = {
    #   "call_count"          : self.call_count,
    #   "total_str_count"     : self.str_count,
    #   "total_prompt_tokens" : self.total_prompt_tokens,
    #   "total_eval_tokens"   : self.total_eval_tokens,
    #   "total_tokens"        : total_tokens,
    #   "elapsed_min"         : round(self.elapsed_min, 3),
    # }
    print("【📊 トークン集計】")
    print(f"呼び出し回数    : {self.call_count}")
    print(f"合計処理時間    : {self.elapsed_min:.2f}分")
    print(f"入力トークン合計: {self.total_prompt_tokens:,}")
    print(f"出力トークン合計: {self.total_eval_tokens:,}")
    print(f"総トークン合計  : {total_tokens:,}")
    print("="*40)
  def meta_data(self):
    prompt_tokens = self.total_prompt_tokens
    eval_tokens = self.total_eval_tokens
    total_tokens = self.total_prompt_tokens + self.total_eval_tokens
    return {
      "meta_data": self.all_records,
      "prompt_tokens": prompt_tokens,
      "eval_tokens": eval_tokens,
      "total_tokens": total_tokens
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
def calc_cost(input_tokens: int, output_tokens: int, model: str) -> dict:
  """
  トークン・コストデータ取得
  """
  price = PRICING.get(model, PRICING["gemini-2.5-flash"])
  input_cost_usd  = (input_tokens  / 1_000_000) * price["input"]
  output_cost_usd = (output_tokens / 1_000_000) * price["output"]
  total_cost_usd  = input_cost_usd + output_cost_usd
  # 為替
  usd_to_jpy = get_usd_to_jpy_yfinance()
  total_cost_jpy  = total_cost_usd * usd_to_jpy
  return {
    "referenc_model": model,
    "input_tokens":    input_tokens,
    "output_tokens":   output_tokens,
    "input_cost_usd":  input_cost_usd,
    "output_cost_usd": output_cost_usd,
    "total_cost_usd":  total_cost_usd,
    "usd_to_jpy":      usd_to_jpy,
    "total_cost_jpy":  total_cost_jpy,
  }
def print_cost_report(cost: dict):
  """
  トークン・コストレポート出力
  """
  print(f"{'='*35}")
  print(f"入力トークン:   {cost['input_tokens']:,}")
  print(f"出力トークン:   {cost['output_tokens']:,}")
  print(f"為替レート:     1 USD = ¥{cost['usd_to_jpy']:.2f}")
  print(f"ベースモデル:    {cost['referenc_model']}")
  print(f"料金 (USD):     ${cost['total_cost_usd']:.6f}")
  print(f"料金 (JPY):     ¥{cost['total_cost_jpy']:.2f}")
  print(f"{'='*35}")
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
def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
  """
  文字列からトークン量計算
  """
  enc = tiktoken.encoding_for_model(model)
  tokens = enc.encode(text)
  return len(tokens)
def splitter_docs_token(splitter_docs):
  """
  ドキュメント分割した推定トークン量の計算
  """
  enc = tiktoken.get_encoding("cl100k_base")
  count_chunk = 0
  count_token = 0
  for i, doc in enumerate(splitter_docs):
    tokens_i = len(enc.encode(doc.page_content))
    count_token += tokens_i
    count_chunk += 1
    #print(f"チャンク{i+1:2d}: {tokens_i}トークン")
  print(f"【合計チャンク数】{count_chunk}")
  print(f"【docs合計トークン:】{count_token}")
  # 推定トークン量の計算
  summary_str = 100 # 1チャンクあたりの推定要約文字数
  estima_total_chars = summary_str * count_chunk # 推定合計文字数
  chars_per_token = len("あ" * summary_str) / len(enc.encode("あ" * summary_str))  # 日本語の比率を計算
  estima_token = int(estima_total_chars / chars_per_token)
  print(f"{'='*35}")
  print(f'【推定トークン量】{estima_token}')
  return estima_token
def text_splitter(docs):
  """
  ドキュメント分割
  """
  ## テクストを分割
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,       # トークンではなく文字数に注意
    chunk_overlap=150,     # 文脈の連続性を確保
    separators=[
      "\n## ", "\n### ",  # 論文の章区切りを優先
      "\n\n", "\n", "。", ".", " ", ""
    ]
  )
  ## ドキュメントを分割
  splitter_docs = text_splitter.split_documents(docs)
  estima_token = splitter_docs_token(splitter_docs)
  return splitter_docs, estima_token
def meta_summary(titles,callback_list):
  """
  call_backのサマリー
  """
  rows = []
  meta_map = {}
  for i in range(len(titles)):
    meta_map[titles[i]] = callback_list[i].meta_data()
  for doc_page, cb in meta_map.items():
    model = cb['meta_data'][0]['model'] if cb['meta_data'] else None
    rows.append({
      'page_name': doc_page,
      'model': model,
      'prompt_tokens': cb['prompt_tokens'],
      'eval_tokens':   cb['eval_tokens'],
      'total_tokens':  cb['total_tokens'],
      'meta_data':     cb['meta_data'],
    })
  df = pd.DataFrame(rows, columns=['page_name', 'model', 'prompt_tokens', 'eval_tokens', 'total_tokens', 'meta_data'])
  return df
## LLMトークン量確認
def token_check (meta_map):
  """
  call_backのmeta情報からトークン量を出力
  """
  for call_neme, meta_data in meta_map.items():
    print("="*40)
    print(f"{call_neme}")
    meta_data.summary()
    cost = calc_cost(
      input_tokens=meta_data.meta_data().get("prompt_tokens"),
      output_tokens=meta_data.meta_data().get("eval_tokens"),
      model="gemini-2.5-flash"
    )
    print_cost_report(cost)