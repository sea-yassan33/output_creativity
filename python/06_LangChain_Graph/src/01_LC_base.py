# ───────────────────────────────
# ライブラリ
# ───────────────────────────────
import sys
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import argparse
# Langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# 共通関数
sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.common import GoogleMetadataCallback, res_output_md
# 定数
load_dotenv()
logger = logging.getLogger(__name__)
# ───────────────────────────────
# モデル設定
# ───────────────────────────────
google_callback = GoogleMetadataCallback()
gemma_api_model = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it",
    google_api_key=os.environ["API_key"],
    temperature=0.5,
    callbacks=[google_callback],
)
# ───────────────────────────────
# プロンプト作成
# ───────────────────────────────
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたは料理の専門家です。
ユーザが入力した料理のレシピを考えて下さい。
""",
        ),
        ("human", "{request}"),
    ]
)
# ───────────────────────────────
# chain作成
# ───────────────────────────────
chain = (
    {"request": RunnablePassthrough()}
    | prompt
    | gemma_api_model
    | StrOutputParser()
)
# ───────────────────────────────
# 実行
# ───────────────────────────────
def main():
    ## argparse
    arg_parser = argparse.ArgumentParser(description="料理レシピ生成ツール")
    arg_parser.add_argument("request", help="料理名を入力します")
    arg_parser.add_argument("--output", default="out", help="結果の出力先")
    args = arg_parser.parse_args()
    ## 出力先パス
    OUTPUT_DIR = args.output
    request = args.request
    try:
        res = chain.invoke(request)
        cb_summary = google_callback.summary()
        res_output_md(res, OUTPUT_DIR, "recipe01")
        res_output_md(cb_summary, dir_str=OUTPUT_DIR, file_name="summary01")
    except Exception:
        logger.exception("レシピ生成に失敗しました")
        sys.exit(1)
if __name__ == "__main__":
    main()