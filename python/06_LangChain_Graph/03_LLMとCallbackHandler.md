# LLMとCallbackHandler

## 1. LLMについて

LangChain の大きな特徴のひとつが、多くの LLM プロバイダーを共通のインターフェースで扱えることです。

Anthropic（Claude）、Google（Gemini）さらにローカルで動く Ollama など、様々な提供元のモデルを、ほぼ同じ書き方で呼び出せます。

たとえばモデルを切り替えたいとき、下記の様に呼び出す部分だけ差し替えれば、その後のコードはほぼそのまま使えます。

```py
# Anthropic に切り替える場合
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-sonnet-4-5")

# Gemini_Developer_APIを使う場合
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemma-4-31b-it")

# ローカル（Ollama）に切り替える場合
from langchain_ollama import ChatOllama
model = ChatOllama(model="gemma4:e4b")

# どちらも同じ書き方で呼べる
response = model.invoke("こんにちは")
```

## 2. ローカルLLMについて

ローカル環境上でAI（大規模言語モデル）を動かす為には`Ollama`というオープンソースツールを使う必要があります。

> ollamaの特徴
- オープンソース
- オフライン対応
- 外部送信がない

### 2-1.ダウンロード

https://ollama.com/download

- インストーラーを実行
- 実行後、ターミナルで下記のコマンドを叩く

```sh
ollama --version
```

### 2-2.モデルをインストール

> 各モデルについて

|シリーズ|URL|
|:----|:----|
|gemma4|https://ollama.com/library/gemma4|
|qwen3.5|https://ollama.com/library/qwen3.5|
|gpt-oss|https://ollama.com/library/gpt-oss|

> インストール方法

```
## モデルをインストール
ollama pull gemma4:e4b
```

### 2-3.Ollama環境設定

> 【参考】スペック

| 項目 | 内容 |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Laptop / VRAM 8GB |
| 実行基盤 | Ollama |
| モデル | Gemma 4 E4B（`gemma4:e4b`） |
| 言語 | Python 3.10+ / LangChain（`langchain-ollama`） |

上記のスペックを例に環境設定を行う

> 環境変数を設定

| 変数名 | 値 |
|---|---|
| `OLLAMA_FLASH_ATTENTION` | `1` |
| `OLLAMA_KV_CACHE_TYPE` | `q8_0` |

`OLLAMA_FLASH_ATTENTION=1`の目的はKV量子化(q8_0) を使えるようにする

`OLLAMA_KV_CACHE_TYPE`の目的はKVキャッシュを半分にして「VRAMの空きを作る」

KVキャッシュを16bit(f16)ではなく8bitで保存し、メモリを半減させる。8GB環境で最も効く設定。

| | 未設定(f16) | q8_0 | q4_0 |
|---|---|---|---|
| KVキャッシュのメモリ | 100%（基準） | **約50%** | 約25% |
| 品質への影響 | なし | ほぼ無し | 小〜中（高コンテキストで目立つ場合あり） |
| 同じVRAMで扱える文脈 | 短い | **約2倍** | 約4倍 |

環境設定完了後はollamaの再起動が必要

> コンテキストの上限を引き上げる

ollamaのデフォルトはVRAM容量に応じて自動で2048〜4096トークン設定されています。

**Ollamaはnum_ctx（コンテキスト）を超えたプロンプトを警告なく黙って切り詰めます**

Modelfileを作成し恒久化します

- `Modelfile` のテキストファイルを作成

```txt
FROM gemma4:e4b
PARAMETER num_ctx 16384
```

- 下記のコマンドを実行

```sh
cd ./ollama
ll Modelfile

ollama create gemma4-e4b-16k -f Modelfile

ollama list

# 以下のコマンドでパラメータ欄「num_ctx」を確認
ollama show gemma4-e4b-16k
```

以後は `gemma4-e4b-16k` を呼ぶだけで常に16Kコンテキストになります。

## 3.CallbackHandlerについて

### 3-1.CallbackHandlerとは

CallbackHandlerは、LLMアプリケーションの実行中に発生する様々なイベントに対して独自の処理をします。

プログラム内部で何が起きているかをリアルタイムで監視・記録が可能になります。

### 3-2.主な役割

- ロギングと監視
- ストリーミング
- デバッグ
- コスト管理
- BaseCallbackHandlerを使用してカスタマイズ

### 3-3.メソッドについて

|メソッド名|実行されるタイミング|
|:----|:----|
|on_llm_start|LLMが処理を開始したとき|
|on_llm_new_token|新しいトークンが生成されたとき（ストリーミング時）|
|on_llm_end|LLMの処理が完了したとき|
|on_chain_start|Chain（一連の処理）が開始されたとき|
|on_tool_start|外部ツール（検索など）が呼び出されたとき|
|on_error|エラーが発生したとき|

### 3-4.ソース例

[common.py](./utils/common.py)
- OllamaMetadataCallback
- GoogleMetadataCallback

### 3-5.使用例

下記の様にどのタイミングで管理するかで、Callbackをセットするパターンが異なります。

```py
# パターン1:LLM呼び出し時に組み込む
callback = OllamaMetadataCallback()
result = chain.invoke(
  {"input_documents": sp_docs}
  ,config={"callbacks": [callback]} #← ここにCallbackをセット
)

#パターン2:LLM初期化時に組み込む
google_callback = GoogleMetadataCallback()
llm_api_gemini = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  google_api_key=os.environ['GOOGLE_AI_ST_API'],
  temperature=0,
  callbacks=[google_callback] #← ここにCallbackをセット
)
```