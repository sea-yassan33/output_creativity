# ローカルLLMの評価について

## 0.Summary

```txt
ローカルLLMでLangChainを使用して、生成処理中の処理状況管理や生成物に対しての評価についてまとめます。
「CallbackHandler」を使用してLLMの呼び出し管理やトークン管理を実装する事が可能になります。
一次評価ではルールベース評価として文字数に対しての評価を行います。
二次評価ではセマンティック評価を行い、エンベンディングを使用してベクトル評価を行います。
三次評価では第二のモデルが生成物を評価する「LLM-as-a-judge」を用いて評価を行います。
```

今回、[参照](#参考)にある論文を基にGoogle翻訳した内容をベースに概要生成から三次評価を行います。

## 1.技術概要

**【GPU】**
- NVIDIA GeForce RTX 4060 Laptop
- 標準メモリ構成: 8 GB

> 参考：上記GPUで動かせるモデル

|モデルサイズ|量子化（圧縮）|動作状況|備考|
|:----|:----|:----|:----|
|1B〜3B (Llama-3.2-3B等)|なし（FP16）|非常に高速|チャット用途でサクサク動きます。|
|7B〜9B (Llama-3, Gemma-2等)|4-bit〜Q8|快適|VRAM 8GBにちょうど収まり、実用的な速度が出ます。|
|12B〜14B (Mistral NeMo等)|Q4_K_M|ギリギリ|VRAMをほぼ使い切ります。他のアプリを開くと速度が落ちます。|
|20B〜|4-bit以上|低速|VRAMから溢れた分がメインメモリ（RAM）に回るため、極端に遅くなります。|

**【ローカルLLMモデル】**
- gemma3:4b
  - Googleが2025年後半にリリース
  - 軽量で高性能なローカルLLM（大規模言語モデル）
  - ローカルPC環境で高速かつ多機能に動作するモデル

**【API:LLMモデル】**
- Gemini 2.5 Flash

> 参考：上記2つのモデルの比較

| 項目 | Gemini 2.5 Flash | Gemma 3 4B |
|------|-----------------|------------|
| 提供形態 | クラウドAPI（有料） | オープンウェイト（無料・ローカル可） |
| コンテキスト長 | **100万トークン** | 12.8万トークン |
| 出力上限 | 65,000トークン | 約8,192トークン |
| 学習データ | 2025年1月まで | 2024年8月まで |
| マルチモーダル | テキスト・画像・動画・音声 | テキスト・画像 |

---

| ユースケース | 推奨モデル |
|------------|-----------|
| 高精度な推論・長文処理が必要 | **Gemini 2.5 Flash** |
| プライバシー重視・ローカル実行 | **Gemma 3 4B** |
| コストを抑えたい・個人利用 | **Gemma 3 4B** |
| 動画・音声の処理が必要 | **Gemini 2.5 Flash** |
| Ollamaなどで手軽に試したい | **Gemma 3 4B** |

**【python: LangChain関連のライブラリ】**

- 今回使用するLangChain関連は下記の通りです。

|ライブラリ名|URL<deps.dev>|
|:----|:----|
|langchain|https://deps.dev/pypi/langchain|
|langchain-google-genai|https://deps.dev/pypi/langchain-google-genai|
|langchain-huggingface|https://deps.dev/pypi/langchain-huggingface|
|langchain-classic|https://deps.dev/pypi/langchain-classic|

> LangChainのバージョンは指定しませんので、インストール前に確認をお願いします。
> LangChain関連以外のライブラリに関して各々インストールを実施してください。

### 共通の関数

- [共通関数](./common_func.py)

## 2.CallbackHandler

- LangChainのCallbackHandlerは、LLMアプリケーションの実行中に発生する様々なイベントに対して独自の処理をします。
- プログラム内部で何が起きているかをリアルタイムで監視・記録が可能になります。

**【CallbackHandlerの主な役割】**
- ロギングと監視
- ストリーミング
- デバッグ
- コスト管理
- BaseCallbackHandlerを使用してカスタマイズが可能

|メソッド名|実行されるタイミング|
|:----|:----|
|on_llm_start|LLMが処理を開始したとき|
|on_llm_new_token|新しいトークンが生成されたとき（ストリーミング時）|
|on_llm_end|LLMの処理が完了したとき|
|on_chain_start|Chain（一連の処理）が開始されたとき|
|on_tool_start|外部ツール（検索など）が呼び出されたとき|
|on_error|エラーが発生したとき|


**BaseCallbackHandlerを用いたカスタマイズ例**

- [OllamaMetadataCallback](./original_func.py)

```py
from langchain_core.callbacks.base import BaseCallbackHandler

# ▼▼▼ Ollam_Callback_Class ▼▼▼
class OllamaMetadataCallback(BaseCallbackHandler):
  """
  Ollama専用callback
  """
  ## 初期化時の処理
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
  ## LLMが処理を開始時の処理
  def on_llm_start(self, serialized, prompts, **kwargs):
    if self.call_count == 0:
      self.start_time = time.time()
    self.str_count += len(prompts[0])
  ## LLMの処理が完了時の処理処理
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
  ## summaryメソッドが呼ばれた際の処理
  def summary(self):
    total = self.total_prompt_tokens + self.total_eval_tokens
    print("\n" + "="*40)
    print("📊 トークン集計")
    print("="*40)
    print(f"呼び出し回数    : {self.call_count}")
    print(f"合計処理時間    : {self.elapsed_min:.2f}分")
    print(f"入力トークン合計: {self.total_prompt_tokens:,}")
    print(f"出力トークン合計: {self.total_eval_tokens:,}")
    print(f"総トークン合計  : {total:,}")
    print("="*40)
  ## meta_dataメソッドが呼ばれた際の処理
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
```

**[Callbackの使用例]**

```py

# パターン1:LLM呼び出し時に読み込む
callback = OllamaMetadataCallback()
result = chain.invoke(
  {"input_documents": sp_docs}
  ,config={"callbacks": [callback]}
)

#パターン2:LLM初期化時に組み込む
google_callback = GoogleMetadataCallback()
llm_api_gemini = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  google_api_key=os.environ['GOOGLE_AI_ST_API'],
  temperature=0,
  callbacks=[google_callback]
)
```

## 3.概要生成とトークン管理

### 実装例

- [概要・トークン管理のプログラム例](./01_概要生成_トークン管理.py)

### 出力例

- [概要生成](./data/test03-summary.md)

> **上記プログラム実行時のトークン量**

```
========================================
llm_call01 ←　1・2回目の呼び出し
【📊 トークン集計】
呼び出し回数    : 2
合計処理時間    : 0.38分
入力トークン合計: 2,277
出力トークン合計: 598
総トークン合計  : 2,875
========================================
===================================
入力トークン:   2,277
出力トークン:   598
為替レート:     1 USD = ¥156.41
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.002178
料金 (JPY):     ¥0.34
===================================
========================================
llm_call02　←　3回目の呼び出し
【📊 トークン集計】
呼び出し回数    : 1
合計処理時間    : 0.19分
入力トークン合計: 631
出力トークン合計: 450
総トークン合計  : 1,081
========================================
===================================
入力トークン:   631
出力トークン:   450
為替レート:     1 USD = ¥156.41
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.001314
料金 (JPY):     ¥0.21
===================================
```

### token-summary

|呼び出し回数|入力トークン|出力トークン|料金(JPY)|
|:----|:----|:----|:----|
|3|2,908|1,048|￥0.55|

## 1・2次評価

一次評価は下記の観点で実施します。
- ルールベース評価
  - 文字数

二次評価は下記の観点で実施します。
- セマンティック評価（Semantic Evaluation）
  - **「意味的に正しいか」**を評価
  - 類似性 (Similarity): 正解例と意味がどれくらい近いか。
  - 忠実性 (Faithfulness): 元データ（知識ソース）に基づいた回答をしているか（ハルシネーションの抑制）

### 実装例

- [1-2次評価実装例](./02_1-2次評価.py)

### 出力例

> ルールベース評価とセマンティック評価

```txt
==================================================
📋 評価の分析Part1
==================================================

【長さの比較】
  生成: 820文字 / 参照: 454文字 (比率: 1.81)
  ✅ 長さは適切

📋 セマンティック評価結果
==================================================
コサイン距離:   0.3133  （0に近いほど良い）
類似度スコア:   0.6867  （1に近いほど良い）
評価結果:       ⚠️ 要改善

```

> 評価用テンプレートを用いて類似度評価を分析

- [評価用テンプレートを用いて類似度評価を分析結果](./out/test03-summary-analysis.md)

> **上記プログラム実行時のトークン量**

```txt
========================================
llm_call2-01
【📊 トークン集計】
呼び出し回数    : 1
合計処理時間    : 0.81分
入力トークン合計: 762
出力トークン合計: 1,747
総トークン合計  : 2,509
========================================
===================================
入力トークン:   762
出力トークン:   1,747
為替レート:     1 USD = ¥156.21
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.004596
料金 (JPY):     ¥0.72
===================================
```

### token-summary

|呼び出し回数|入力トークン|出力トークン|料金(JPY)|
|:----|:----|:----|:----|
|1|762|1747|￥0.72|

## 3次評価

三次評価はLLM-as-a-judgeを使用して評価します。

### LLM-as-a-judgeについて

人間や従来のプログラムの代わりに、LLM（大規模言語モデル）を使って他のLLMの出力を評価・採点させる手法です

- LangChainの「load_evaluator」を使用

```py
from langchain_classic.evaluation import load_evaluator

# 【labeled_criteria評価でパターン】
evaluator = load_evaluator(
  "labeled_criteria",　# 第一引数（必須）：評価器の種類
  llm=llm,　# モデルを指定
  criteria="correctness" # 「labeled_criteria」設定時に組み込み基準をいれる
)

# 【複数の評価指標を指定するパターン】
## 評価指標をmap形式で用意する
criteria_list = {
  "conciseness":  "概要は簡潔にまとめられているか？",
  "completeness": "重要なポイントが網羅されているか？",
}
## 評価結果を格納する箱(List形式)を用意
result_criteria_list = []
for name, description in criteria_list.items():
  evaluator = load_evaluator(
    "criteria",　# ←入力＋予測のみで評価
    llm=llm_api_gemini,
    criteria={name: description}# ←評価基準を格納
  )
  ## 設定評価基準毎に評価を実施
  result = evaluator.evaluate_strings(
    prediction=generated_summary,
    input=paper_text
  )
  ## 評価結果を格納
  result_criteria_list.append(result)
```

> 第一引数の値について

|設定値|用途|
|:----|:----|
|criteria|入力＋予測のみで評価（参照テキスト不要）|
|labeled_criteria|参照テキスト(reference)も使って評価|
|embedding_distance|Embeddingベースの類似度評価|
|pairwise_criteria|モデルA vs モデルBの出力比較|
|qa|Q&A形式の正確性評価,reference必須,参照テキストとの比較|
|cot_qa|Chain-of-Thought付きQ&A評価|


> 評価器の種類load_evaluator時、criteriaのパラメータについて

|設定値|用途|
|:----|:----|
|correctness|参照テキストと比較して正確か判断。期待されるデータを入れる必要あり。（labeled_criteria専用）|
|conciseness|簡潔にまとめられているか|
|completeness|重要なポイントが網羅されているか|
|relevance|入力に対して関連性があるか|
|coherence|論理的な流れ・一貫性があるか|
|helpfulness|役に立つ内容か|
|depth|内容に深みがあるか|
|harmfulness|有害な内容が含まれていないか|
|maliciousness|悪意のある内容が含まれていないか？|
|controversiality|議論を呼ぶ内容か|

> Embeddingベースの類似度評価時に用いる測定法

|設定値|用途|メトリクス | 特徴 | スコア範囲 |
|:----|:----|:----|:----|:----|
|EmbeddingDistance.COSINE|デフォルト・自然言語に最適|`COSINE` | 方向の類似度・長さに依存しない | 0〜2（通常0〜1） |
|EmbeddingDistance.EUCLIDEAN|直線距離|`EUCLIDEAN` | ベクトル間の直線距離 | 0〜∞ |
|EmbeddingDistance.MANHATTAN|絶対値の差の合計|`MANHATTAN` | 各次元の差の絶対値合計 | 0〜∞ |
|EmbeddingDistance.CHEBYSHEV|各次元の最大差|`CHEBYSHEV` | 各次元の最大差 | 0〜∞ |

### 実装例

- [3次評価実装例](./03_3次評価.py)

### 出力例

reference評価（参照テキスト(reference)も使って評価）とcriteria（簡潔さ・完全性）の評価サマリー内容になります。

- [reference評価とcriteriaのsummary内容](./out/test04-assesment_summary.md)

> **上記プログラム実行時のトークン量**

```txt
========================================
llm_call3-01
【📊 トークン集計】
呼び出し回数    : 1
合計処理時間    : 0.17分
入力トークン合計: 3,036
出力トークン合計: 1,745
総トークン合計  : 4,781
========================================
===================================
入力トークン:   3,036
出力トークン:   1,745
為替レート:     1 USD = ¥156.37
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.005273
料金 (JPY):     ¥0.82
===================================
========================================
llm_call3-02
【📊 トークン集計】
呼び出し回数    : 1
合計処理時間    : 0.29分
入力トークン合計: 340
出力トークン合計: 400
総トークン合計  : 740
========================================
===================================
入力トークン:   340
出力トークン:   400
為替レート:     1 USD = ¥156.37
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.001102
料金 (JPY):     ¥0.17
===================================
========================================
llm_call3-03
【📊 トークン集計】
呼び出し回数    : 2
合計処理時間    : 0.47分
入力トークン合計: 5,591
出力トークン合計: 5,016
総トークン合計  : 10,607
========================================
===================================
入力トークン:   5,591
出力トークン:   5,016
為替レート:     1 USD = ¥156.37
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.014217
料金 (JPY):     ¥2.22
===================================
========================================
llm_call3-04
【📊 トークン集計】
呼び出し回数    : 2
合計処理時間    : 0.48分
入力トークン合計: 1,421
出力トークン合計: 1,362
総トークン合計  : 2,783
========================================
===================================
入力トークン:   1,421
出力トークン:   1,362
為替レート:     1 USD = ¥156.37
ベースモデル:    gemini-2.5-flash
料金 (USD):     $0.003831
料金 (JPY):     ¥0.60
===================================
```

### token-summary

|呼び出し回数|入力トークン|出力トークン|料金(JPY)|
|:----|:----|:----|:----|
|6|10,388|8,523|￥3.81|


## 総括

> 今回、各セクションで使用されたトークン量と料金（gemini-2.5-flashベース）は下記のとおりです。

|セクション|呼び出し回数|入力トークン|出力トークン|料金(JPY)|
|:----|:----|:----|:----|:----|
|概要生成|3|2,908|1,048|￥0.55|
|2次評価|1|762|1,747|￥0.72|
|3次評価|6|10,388|8,523|￥3.81|
||||||
|合計|9|14,058|11,318|￥4.37|

> 今回、論文の概要生成から3次評価までLLMモデルを9回呼び出し、「gemini-2.5-flash」をベースに試算した結果4.37円かかる計算となりました。

> 1次評価でテンプレートは500文字以内と書いてるのに実際は820文字出力されている結果となりました。テンプレートの調整や文章校正用のLLMが必要と思われます

> 3次評価の結果において参照テキストと比較して正確性の観点で「合格」判定となりました。

> 様々な評価指標があるため、何を目的に評価をしているのか明確にし、それに応じて評価方法（パラメータ）を調整する必要と思われます。

## 参考
- [Amplifiers or Equalizers? A Longitudinal Study of LLM Evolution in Software Engineering Project-Based Learning](https://arxiv.org/abs/2511.23157)