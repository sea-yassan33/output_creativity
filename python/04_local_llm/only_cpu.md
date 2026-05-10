# CPUのみで動かす場合

CPUのみで動かす場合のモデルや簡単なLangChainの実装方法について紹介します。

# CPUのみでの動作要件

> Gemma 3の最大の特徴は、一般的なPCのCPUのみで非常に高速に動作する点です。
> Ollamaでの推論エンジンを使用した場合の目安です。

| 項目 | Gemma 3: 270M | Gemma 3: 1B | 備考 |
| --- | --- | --- | --- |
| **推奨メモリ (RAM)** | 2GB 以上 | 4GB 以上 | 8GBあれば他の作業も快適です |
| **ディスク容量** | 約 0.5GB | 約 1.5GB ~ 2GB | 量子化(4-bit)済みのサイズ目安 |
| **CPU性能目安** | Intel Core i3 / Ryzen 3 以上 | Intel Core i5 / Ryzen 5 以上 | AVX2対応CPUであれば高速です |
| **推論速度 (目安)** | 50〜100+ tokens/sec | 20〜50+ tokens/sec | 人間の読書速度を大幅に超えます |
| **想定用途** | CLIツール、単純な分類、翻訳 | チャットボット、コード補助 | 低消費電力・高レスポンス |

# LLMモデル性能比較表

> Gemini2.5-Flashをベンチマークにモデル性能比較表となります。

| 項目 | Gemma3:270M | Gemma3:1B | **Gemma3:4B** | Gemini2.5-Flash |
| --- | --- | --- | --- | --- |
| **モデルタイプ** | オープンウェイト | オープンウェイト | **オープンウェイト** | クラウドAPI |
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

- [Gemma3:1Bの実用性](https://zenn.dev/fumi_mizu/articles/397cafc747bfe7)

# Ollamaダウンロードと使用方法

## Ollamaのサイトでダウンロード
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

```sh
pip install python-dotenv

pip install langchain
pip install langchain-community
pip install langchain-core
```

# 実装

> 開発環境
- OS：windows11
- プロセッサー：Intel(R) N95 1.70 GHz
- RAM:16GB（8GM）

## envファイルを作成
```txt
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

## 3.テンプレートを作成
```py
# template と chain
prompt = ChatPromptTemplate.from_messages(
  [
    ("system","ユーザが入力した料理のレシピを考えて下さい"),
    ("human","{dish}"),
  ]
)
## LCEL「|」で連結し、chainを作成
chain = prompt | ollama_llm | StrOutputParser()
```

## 4.callback設置し、LLMを呼び出す
```py
# 実行
callback = OllamaMetadataCallback()
res = chain.invoke(
  {"dish":"チーズケーキ"},
  config={"callbacks": [callback]}
)
```

## 5.結果を出力
```py
## md形式出力
commonFunc.res_output_md(response=res,file_name="test-01")
callback.summary()
```

### gemma3:1bの出力例

> markDown出力例

[test-01.md](./sample/out/test-01-1b.md)

> callbackサマリー

```txt
==============================
【呼び出しサマリー】
呼び出し回数    : 1
合計処理時間    : 1.16分
入力トークン合計: 26
出力トークン合計: 794
総トークン合計  : 820
==============================
```

> **gemma3:1b**はギリギリ動く程度。他のアプリは閉じた方がいいレベル。

### callbac出力例（gemma3:270m）

> markDown出力例

[test-01.md](./sample/out/test-01-270m.md)

> callbackサマリー

```txt
==============================
【呼び出しサマリー】
呼び出し回数    : 1
合計処理時間    : 0.35分
入力トークン合計: 23
出力トークン合計: 496
総トークン合計  : 519
==============================
```

> **gemma3:270m**は少々カクカクしていますが、他のアプリが動作しても動くレベル。