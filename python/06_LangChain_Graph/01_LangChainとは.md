# LangChainとは

## 1. LangChainについて

- ChatGPTなどの大規模言語モデルの機能拡張を効率的に実装するためのライブラリです。
- 大規模言語モデル（LLM）を活用し、高度なAIアプリケーションを効率的に開発できるように設計されたオープンソースのフレームワークです。

https://www.langchain.com

>  公式ドキュメント

https://docs.langchain.com

## 2. LangChainの６つの機能

- Model I/O:OpenAIをはじめとした様々な言語モデル・チャットモデル・エンべディングモデルを切り替えたり、組み合わせたりすることができる機能
- Retrieval:言語モデルが学習していない事柄に関して、外部データを用いて、回答を生成するための機能
- Chains:複数のプロンプトに分けて、順番に実行することで、より精度の高い回答が得られます。
- Memory:ChainsやAgentsの内部における状態保持をする機能
- Agents:言語モデルに渡されたツールを用いて、モデル自体が、次にどのようなアクションを取るかを決定・実行・観測・完了するまで繰り返す機能
- Callbacks:大規模言語モデルのアプリケーションのロギング、モニタリング、非同期処理などを効率的に管理する機能

## 3. LangChainの全体構成

- LangChainライブラリ
  - PythonおよびJavaScript（TypeScript）のライブラリ
- LangChain Templates
  - 一般的なチャットツールなどで使われる機能のテンプレートが用意されています
- LangServe
  - LangChainにおけるRunnablesとChainsをREST APIとしてデプロイするためのライブラリです
- LangSmith
  - 機能をデバッグ、テスト、評価、モニタリングできる開発者プラットフォーム

![全体構造](https://i.gyazo.com/fab171e036cb954ba1a303cca41dde43.png)

## 4. LCELについて

- LCEL（LangChain Expression Language）とは、LangChain特有のChainsを実装するための新しい記法です。
- Chainsはコンポーネントと呼ばれる、プロンプトのテンプレート（以下ではpromptと定義）やモデルのインスタンス（以下ではllmと定義）を | で繋ぐことで構成されます。

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# モデルの定義
model = ChatGoogleGenerativeAI(model= "gemini-2.5-flash",
                                google_api_key="API_KEYをセット",
                                temperature=0.7)

# プロンプトの定義
prompt = ChatPromptTemplate.from_template(
    "以下の質問に答えてください: {question}"
)

# StrOutputParserの定義
output_parser = StrOutputParser()

# LCELによるChainsの定義
chain = prompt | llm | output_parser

# Chainの実行
response = chain.invoke({"question": "こんにちは"})

print(response)
```