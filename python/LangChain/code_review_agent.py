## ライブラリ
import os
from dotenv import load_dotenv
load_dotenv()
## LangChain系ライブラリ
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
## model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.environ['GOOGLE_AI_ST_API'], temperature=0)
## プロンプトを定義
prompt = ChatPromptTemplate.from_messages([
  ("system", """あなたは熟練のシニアエンジニアです。
  ユーザがレビュー依頼があったコードに対してレビューを行い。以下のフォーマットでレポートを返してください。
  ## フォーマット
  正確性スコア：（得点）/10<br/>
  可読性スコア：（得点）/10<br/>
  安全性スコア：（得点）/10<br/>
  【詳細なコードレビューのフィードバック】<br/>
  
  （フィードバックの内容）

  【修正案】<br/>

  （修正する内容）
  """),
  ("user", "以下のコードをレビューしてください:\n{source_code}")
])
## チェーン
chain = prompt | model | StrOutputParser()
# レビュー対象のファイルを指定
loader = TextLoader("./sample/review_subject.js", encoding="utf-8")
docs = loader.load()
# 実行
result = chain.invoke({
    "source_code": docs[0].page_content, # レビュー対象の文字列が入ります
})
## 出力
if not os.path.exists("./out"):
  os.makedirs("./out")
with open(f"./out/code_review_agent.md", "w", encoding="utf-8") as f:
  f.write(result)