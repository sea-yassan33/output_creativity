import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
import os
from dotenv import load_dotenv
load_dotenv(".env")
# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# LLM
llm = ChatGoogleGenerativeAI(model= "gemini-2.5-flash",google_api_key=os.environ['GOOGLE_AI_ST_API'],temperature=0.7)
# LangFuse
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler
# コンストラクタ引数を使用してLangfuseクライアントを初期化します。
Langfuse(
  public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
  secret_key=os.environ["LANGFUSE_SECRET_KEY"],
  host=os.environ["LANGFUSE_BASE_URL"]
)
# 設定済みのクライアントインスタンスを取得します
langfuse = get_client()
# langfuseハンドラを初期化します
langfuse_handler = CallbackHandler()
# markDown形式出力用関数
def res_output_md(response,file_name):
  ## outフォルダがない場合は作成
  if not os.path.exists("./out"):
    os.makedirs("./out")
  with open(f"./out/{file_name}.md", "w", encoding="utf-8") as f:
    f.write(response)
## prompを作成
prompt = ChatPromptTemplate.from_messages(
  [
    ("system","ユーザが入力した料理のレシピを考えて下さい"),
    ("human","{dish}"),
  ]
)
## Chainを作成
chain = prompt | llm | StrOutputParser()
## Chain実行
res = chain.invoke({"dish":"カレーライス"}, config={"callbacks": [langfuse_handler]})
## ログデータを送信をLangFuseに送信
langfuse.flush()
# ▼▼▼ 出力関連 ▼▼▼
res_output_md(res,"res01")