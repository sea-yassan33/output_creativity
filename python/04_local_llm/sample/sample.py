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
# template と chain
prompt = ChatPromptTemplate.from_messages(
  [
    ("system","ユーザが入力した料理のレシピを考えて下さい"),
    ("human","{dish}"),
  ]
)
## LCEL「|」で連結し、chainを作成
chain = prompt | ollama_llm | StrOutputParser()
# 実行
callback = OllamaMetadataCallback()
res = chain.invoke(
  {"dish":"チーズケーキ"},
  config={"callbacks": [callback]}
)
## md形式出力
commonFunc.res_output_md(response=res,file_name="test-01")
callback.summary()