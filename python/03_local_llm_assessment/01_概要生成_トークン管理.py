import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True
import os
from dotenv import load_dotenv
load_dotenv()
import common_func
from common_func import OllamaMetadataCallback
## LangChain系ライブラリ
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
## model
llm = ChatOllama(model="gemma3:4b",base_url=os.environ['OLLAM_URL'],temperature=0.0)
## 定数
meta_map = {}
# ============================================================
# Step 0: 準備
# ============================================================
with open("./data/paper01_maintext.md", "r", encoding="utf-8") as f:
  text = f.read()
token_count = common_func.count_tokens(text)
print(f"トークン数: {token_count:,}")
print(f"文字数: {len(text):,}")
print(f"トークン/文字 比率: {token_count / len(text):.2f}")
# ============================================================
# Step 1: テンプレート準備
# ============================================================
## 各チャンク毎に要点を生成する際のテンプレート
map_prompt = ChatPromptTemplate.from_template("""
以下のテキストの要点を簡潔にまとめてください：

{chunk}

要点：
""")
## 最終的に概要生成する際のテンプレート
reduce_prompt = ChatPromptTemplate.from_template("""
以下の複数の要点をまとめて、論文全体の概要を500字以内で作成してください：

{summaries}

最終概要：
""")
# ============================================================
# Step 2: テキストの分割処理
# ============================================================
loader = TextLoader("./data/paper01_maintext.md", encoding="utf-8")
docs = loader.load()
## テキストを分割
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=3000,       # トークンではなく文字数に注意
  chunk_overlap=300,     # 文脈の連続性を確保
  separators=[
    "\n## ", "\n### ",  # 論文の章区切りを優先
    "\n\n", "\n", "。", ".", " ", ""
  ]
)
## ドキュメントを分割
splitter_docs = text_splitter.split_documents(docs)
print(f'【チャンク数】{len(splitter_docs)}')
# ============================================================
# Step 3: 各チャンク毎に要点を生成
# ============================================================
chunk_summaries = []
chain = map_prompt | llm | StrOutputParser()
callback = OllamaMetadataCallback()
for i, chunk in enumerate(splitter_docs):
  summary = chain.invoke({"chunk": chunk},config={"callbacks": [callback]})
  chunk_summaries.append(summary)
  print(f"チャンク {i+1}/{len(splitter_docs)} 完了")
# callbackの情報をmap形式で格納
meta_map["llm_call01"] = callback
## 各チャンクで生成した要点を統合
combined = "\n\n".join(chunk_summaries)
# ============================================================
# Step 4: 最終の概要を生成
# ============================================================
chain02 = reduce_prompt | llm | StrOutputParser()
callback = OllamaMetadataCallback()
final_summary = chain02.invoke({"summaries": combined},config={"callbacks": [callback]})
# callbackの情報をmap形式で格納
meta_map["llm_call02"] = callback
# ============================================================
# Step 5: 生成コンテンツの出力とトークン量の確認
# ============================================================
## 生成コンテンツ出力（評価時に使用）
common_func.res_output_md(response=final_summary,dir_str="data",file_name=f"test03-summary")
## LLMトークン量確認
common_func.token_check(meta_map)