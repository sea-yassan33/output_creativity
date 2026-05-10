import time
from pathlib import Path
from langchain_core.callbacks.base import BaseCallbackHandler
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
    print("="*30)
    print("【コールバックsummary】")
    print(f"呼び出し回数    : {self.call_count}")
    print(f"合計処理時間    : {self.elapsed_min:.2f}分")
    print(f"入力トークン合計: {self.total_prompt_tokens:,}")
    print(f"出力トークン合計: {self.total_eval_tokens:,}")
    print(f"総トークン合計  : {total:,}")
    print("="*30)
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