import os
from dotenv import load_dotenv
load_dotenv()
# Langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# Geminiモデル
llm_gemini = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  google_api_key=os.environ['API_KEY'],
  temperature=0.5
)
import common
from common import GoogleMetadataCallback
# =================================
# 準備フェーズ
# =================================
# レビュー対象のコードを用意
with open("./data/sample.js", "r", encoding="utf-8") as f:
  source_text = f.read()
# テンプレート用意
review_prompt = ChatPromptTemplate.from_template("""
あなたは熟練のシニアエンジニアです。
以下のJavaScriptコードをレビューを行ってください。
```js
{source_code}
```

そのレビュー結果を下記のフォーマット(markdowon形式)でレポートを返してください。
```md
正確性スコア：（得点）/10<br/>
可読性スコア：（得点）/10<br/>
安全性スコア：（得点）/10<br/>
【詳細なコードレビューのフィードバック】<br/>

（フィードバックの内容）

【修正案】<br/>

（修正する内容）
```

""")
# =================================
# 実行フェーズ
# =================================
## LCEL「|」で連結し、chainを作成
chain = review_prompt | llm_gemini | StrOutputParser()
# callbackを準備
callback = GoogleMetadataCallback()
# 実行
res = chain.invoke(
  {"source_code":source_text},
  config={"callbacks": [callback]}
)
## md形式出力
common.res_output_md(response=res,file_name="test-reveiw")
summary_md = callback.summary()