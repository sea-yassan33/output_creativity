# 【LangChain】コードレビューエージェント

## はじめに
- 生成AIでなんでもコードを生成できる中、一般的な規約や組織内の規約に沿った観点でレビューを出す必要があると思いました。
- そこで、評価観点を基にコードレビューレポートを生成するエージェントを作成しました。

## 前提条件

- LangChainの必要なライブラリがインストール済みであること

## 今回使用するLangChain系ライブラリ

```python
## LangChain系ライブラリ
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
```

## レビュー対象のサンプルコード

[レビュー対象のサンプルコード](../LangChain/sample/review_subject.js)

## 実装

[code_review_agent.py](../LangChain/code_review_agent.py)

## 出力例

[出力例](../LangChain/out/code_review_agent.md)

## 後記
- 今回はRAG（検索拡張生成）の仕組みは取り入れてはいませんが、RAGを入れることでチーム内・組織内の規約に沿ったコードレビュー生成をしてくれると思います。
- コードレビューにかける時間や負担の軽減に繋がるのではないかと思いました。
- チームリーダにレビュー依頼を出す前に一度レポートを出してもらったり、「修正案は出さないで」と指示しといてエンジニア育成にも使えるのではと思いました。
- 外部に流出させてはいけないコードに関しては場合はローカルLLM環境を作成する必要があると思いました。