# CPUのみで動かす場合

CPUのみで動かす場合のモデルやLangChainを使用した実装例を紹介します。

# CPUのみでの動作要件

> Gemma3の最大の特徴は、一般的なPCのCPUのみで非常に高速に動作する点です。
> Ollamaでの推論エンジンを使用した場合の目安です。

| 項目 | Gemma3: 270M | Gemma3: 1B |
| --- | --- | --- |
| **推奨メモリ (RAM)** | 2GB 以上 | 4GB 以上 |
| **ディスク容量** | 約 0.5GB | 約 1.5GB ~ 2GB |
| **CPU性能目安** | Intel Core i3 / Ryzen 3 以上 | Intel Core i5 / Ryzen 5 以上 |
| **推論速度 (目安)** | 50〜100+ tokens/sec | 20〜50+ tokens/sec |
| **想定用途** | CLIツール、単純な分類、翻訳 | チャットボット、コード補助 |

# LLMモデル性能比較表

> Gemini2.5-Flashをベンチマークにモデル性能比較表となります。

| 項目 | Gemma3:270M | Gemma3:1B | **Gemma3:4B** | Gemini2.5-Flash |
| --- | --- | --- | --- | --- |
| **モデルタイプ** | オープンウェイト | オープンウェイト | **オープンウェイト** | クラウドAPI |
| **CPU/GPU** | CPUのみ可 | CPUのみ可 | **GPU必要** | ー（API実行） |
| **パラメータ数** | 2.7億 | 10億 | **40億** | 非公開 |
| **得意なタスク** | 単純な要約、補完 | 指示追従、論理思考 | **高度な推論、データ処理** | 複雑な推論、広域分析 |
| **コーディング性能** | 単一関数の補完 | 関数の実装、テスト生成 | **複数ファイルの構成提案、デバッグ** | システム設計、リポジトリ理解 |
| **HumanEval (参考：コーディング能力)** | 低 | 中 | **中〜高（実用レベル）** | 高 |
| **コンテキスト長** | 32k tokens | 128k tokens | **128k tokens** | 1M tokens |
| **マルチモーダル** | 対応（画像 | 対応（画像） | **対応（画像）** | 対応（全般） |
| **知識量・正確性** | 限定的 | 一般的 | **高い（専門知識の理解）** | 非常に高い |

> Gemma3:270M: エディタのリアルタイム補完（オートコンプリート）など、超低遅延が求められる用途に適しています。

> Gemma3:1B: ローカル環境でのちょっとしたPythonスクリプトの作成や、ユニットテストの生成に実用的なレベルです。

> **Gemma3:4B**: コード生成の質が1Bから飛躍的に向上しており、日常的な開発の補助として最もバランスが良いサイズです。

> [【参考】Gemma3:1Bの実用性](https://zenn.dev/fumi_mizu/articles/397cafc747bfe7)

# Ollamaダウンロードと使用方法

## Ollamaサイトでダウンロード
https://ollama.com/download

- インストーラーを実行
- 実行後、ターミナルで下記のコマンドを叩く
```sh
ollama --version
```

## Gemma3モデルをインストール

```sh
## Gemma3モデルをインストール(2つのモデル)
ollama pull gemma3:1b
ollama pull gemma3:270m
```

# python環境構築

## ライブラリインストール

- 以下のライブラリーをインストールします。

|ライブラリ名|URL<deps.dev>|
|:----|:----|
|python-dotenv|https://deps.dev/pypi/python-dotenv|
|langchain|https://deps.dev/pypi/langchain|
|langchain-community|https://deps.dev/pypi/langchain-community|
|langchain-core|https://deps.dev/pypi/langchain-core|

```sh
pip install python-dotenv

pip install langchain
pip install langchain-community
pip install langchain-core
```

# 実装例

> 実装環境（実行モデル：**gemma3:270m**・**gemma3:1b**）
- OS：windows11
- プロセッサー：Intel N95
- RAM:16GB（8GM）

## envファイルを作成
```sh
OLLAM_BASE='http://localhost:11434'
```

> Ollamaのデフォルトポート番号は「11434」 

## 1.必要なライブラリを読み込む
```py
import sys
sys.dont_write_bytecode = True
import os
from dotenv import load_dotenv
load_dotenv(".env")
import commonFunc
from commonFunc import OllamaMetadataCallback
## LangChain系ライブラリ
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
```

## 2.modelを読み込む
```py
## model
#model_str = "gemma3:270m"
model_str = "gemma3:1b"
ollama_llm = ChatOllama(model=model_str,base_url=os.environ['OLLAM_BASE'],temperature=0.0)
```

## 3.レビュー対象のサンプルコードを用意

[【サンプル：レビュー対象JSファイル】 sample.js](./sample/data/sample.js)

```py
# レビュー対象のコードを用意
with open("./data/sample.js", "r", encoding="utf-8") as f:
  source_text = f.read()
```

## 4.テンプレートを作成
```py
review_prompt = ChatPromptTemplate.from_template("""
あなたは熟練のシニアエンジニアです。
以下のJavaScriptコードをレビューを行ってください。
---js
{source_code}
---

そのレビュー結果を下記のフォーマット(markdowon形式)でレポートを返してください。
---md
正確性スコア：（得点）/10<br/>
可読性スコア：（得点）/10<br/>
安全性スコア：（得点）/10<br/>
【詳細なコードレビューのフィードバック】<br/>

（フィードバックの内容）

【修正案】<br/>

（修正する内容）
---
""")
```

## 5.Chainを作成
```py
## LCEL「|」で連結し、chainを作成
chain = review_prompt | ollama_llm | StrOutputParser()
```

## 4.callback設置し、LLMを呼び出す
```py
# 実行
callback = OllamaMetadataCallback()
res = chain.invoke(
  {"source_code":source_text},
  config={"callbacks": [callback]}
)
```

## 5.結果を出力
```py
## md形式出力
myfunc.res_output_md(response=res,file_name="test-reveiw")
callback.summary()
```

---

### callbac出力例（gemma3:270m）

> markDown出力例

[test-reveiw-270m.md](./sample/out/test-reveiw-270m.md)

> callbackサマリー

```txt
==============================
【コールバックsummary】
呼び出し回数    : 1
合計処理時間    : 0.48分
入力トークン合計: 516
出力トークン合計: 809
総トークン合計  : 1,348
==============================
```

> **gemma3:270m**は止まることなく動いている印象です。

> スコアリングはしてくれず、コードレビューも適格な指摘はされておりませんでした。

---

### gemma3:1bの出力例

> markDown出力例

[test-reveiw-1b.md](./sample/out/test-reveiw-1b.md)

> callbackサマリー

```txt
==============================
【コールバックsummary】
呼び出し回数    : 1
合計処理時間    : 1.67分
入力トークン合計: 475
出力トークン合計: 1,180
総トークン合計  : 1,655
==============================
```

> **gemma3:1b**は何とか動くレベル。

> スコアは怪しく、レビューは指示通り出力してくれました。

---

### gemma3:4bの出力例（参考：GPU使用）

> 実装環境（実行モデル：**gemma3:4b**）
- OS：windows11
- プロセッサー：13thGen IntelCore i7
- RAM:32GB（31GM）
- GPU:NVIDIA GeForce RTX 4060 Laptop(8 GB)

> markDown出力例

[test-reveiw-4b.md](./sample/out/test-reveiw-4b.md)

> callbackサマリー

```txt
==============================
【コールバックsummary】
呼び出し回数    : 1
合計処理時間    : 0.45分
入力トークン合計: 475
出力トークン合計: 1,186
総トークン合計  : 1,661
==============================
```

> **gemma3:4b**はGPUを使用しているます。動きは気になることなくスムーズです。

> スコア・レビューは指示通り出力してくれます。