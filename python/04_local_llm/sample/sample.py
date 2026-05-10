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
## model
#model_str = "gemma3:270m"
model_str = "gemma3:1b"
ollama_llm = ChatOllama(model=model_str,base_url=os.environ['OLLAM_URL'],temperature=0.0)
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
## LCEL「|」で連結し、chainを作成
chain = review_prompt | ollama_llm | StrOutputParser()
# 実行
callback = OllamaMetadataCallback()
res = chain.invoke(
  {"source_code":source_text},
  config={"callbacks": [callback]}
)
## md形式出力
#commonFunc.res_output_md(response=res,file_name="test-reveiw-270m")
commonFunc.res_output_md(response=res,file_name="test-reveiw-1b")
callback.summary()