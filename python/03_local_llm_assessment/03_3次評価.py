import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
import sys
sys.dont_write_bytecode = True
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import common_func
from common_func import GoogleMetadataCallback
from common_func import OllamaMetadataCallback
## LangChain系ライブラリ
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.evaluation import load_evaluator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
## model
llm = ChatOllama(model="gemma3:4b",base_url=os.environ['OLLAM_URL'],temperature=0.0)
## 定数
meta_map = {}
result_map ={}
##　関数
def print_evaluation_report_markdown(df: pd.DataFrame) -> str:
  """
  サマリーをmarkdown形式で出力
  """
  lines = []
  # ============================================================
  # ヘッダー
  # ============================================================
  lines.append("# 📋 論文概要 評価レポート\n")
  # 合否サマリーテーブル
  lines.append("## 評価サマリー\n")
  lines.append("| 評価項目 | スコア | 合否 | 判定 |")
  lines.append("|----------|--------|------|------|")
  for _, row in df.iterrows():
    judge = '✅ 合格' if row['score'] == 1 else '❌ 不合格'
    lines.append(
      f"| {row['evaluation_label']} "
      f"| {row['score']} "
      f"| {row['value']} "
      f"| {judge} |"
    )
  total = df['score'].sum()
  lines.append(f"\n**総合スコア: {total} / {len(df)}**\n")
  lines.append("---\n")
  # ============================================================
  # 各評価の詳細
  # ============================================================
  lines.append("## 評価詳細\n")
  for _, row in df.iterrows():
    label     = row['evaluation_label']
    score     = row['score']
    value     = row['value']
    reasoning = row['reasoning']
    # reasoningの前置き文を除去
    skip_prefixes = [
      "以下のように自然な日本語に翻訳しました",
      "以下は、提示された内容をより自然な日本語に翻訳したものです",
      "以下は、提供されたテキストをより自然な日本語に翻訳したものです",
      "---",
      "**注記:**",
    ]
    cleaned_lines = []
    for line in reasoning.strip().split('\n'):
      if any(line.strip().startswith(p) for p in skip_prefixes):
        continue
      cleaned_lines.append(line)
    cleaned_reasoning = '\n'.join(cleaned_lines).strip()
    judge = '✅ 合格' if score == 1 else '❌ 不合格'
    lines.append(f"### 【{label}】{judge}\n")
    lines.append(f"| 項目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 評価スコア | `{score}` |")
    lines.append(f"| 合格/不合格 | `{value}` |")
    lines.append(f"\n#### 評価内容\n")
    lines.append(cleaned_reasoning)
    lines.append("\n---\n")
  return '\n'.join(lines)
# ============================================================
# Step 1: 論文の本文・期待する概要・生成された概要を読み込む
# ============================================================
## 論文の本文
with open("./data/paper01_maintext.md", "r", encoding="utf-8") as f:
  paper_text = f.read()
## 期待する概要
with open("./data/paper01_oberveiw.md", "r", encoding="utf-8") as f:
  reference_summary = f.read()
## 生成された概要
with open("./data/test03-summary.md", "r", encoding="utf-8") as f:
  generated_summary = f.read()
# ============================================================
# Step 2:labeled_criteria評価＜参照テキスト(reference)を用いる＞
# （Call回数：1回）
# ============================================================
google_callback = GoogleMetadataCallback()
llm_api_gemini = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  google_api_key=os.environ['GOOGLE_AI_ST_API'],
  temperature=0,
  callbacks=[google_callback]
)
labeled_evaluator = load_evaluator(
  "labeled_criteria", # 評価器の種類
  llm=llm_api_gemini, # 評価に使うLLM
  criteria="correctness" 
)
labeled_result = labeled_evaluator.evaluate_strings(
  prediction=generated_summary,
  input=paper_text,
  reference=reference_summary,
)
meta_map["llm_call3-01"] = google_callback
## 結果を翻訳
trans_prompt = ChatPromptTemplate.from_template(
      "以下を自然な日本語に翻訳してください:\n{text}"
  )
ollma_callback = OllamaMetadataCallback()
chain = trans_prompt | llm | StrOutputParser()
trans_result = chain.invoke(
  {"text": labeled_result['reasoning']},
  config={"callbacks": [ollma_callback]}
)
meta_map["llm_call3-02"] = ollma_callback
result01 = [labeled_result['score'],labeled_result['value'],trans_result]
result_map["result01"] =result01
# ============================================================
# Step 3: criteria評価＜入力＋予測のみで評価＞
# ============================================================
google_callback = GoogleMetadataCallback()
llm_api_gemini = ChatGoogleGenerativeAI(
  model="gemini-2.5-flash",
  google_api_key=os.environ['GOOGLE_AI_ST_API'],
  temperature=0,
  callbacks=[google_callback]
)
criteria_list = {
  "conciseness":  "概要は簡潔にまとめられているか？",
  "completeness": "重要なポイントが網羅されているか？",
}
result_criteria_list = []
for name, description in criteria_list.items():
  evaluator = load_evaluator("criteria",llm=llm_api_gemini, criteria={name: description})
  result = evaluator.evaluate_strings(
    prediction=generated_summary,
    input=paper_text
  )
  result_criteria_list.append(result)
meta_map["llm_call3-03"] = google_callback
## 結果を翻訳
ollma_callback = OllamaMetadataCallback()
chain = trans_prompt | llm | StrOutputParser()
trans_result_list = []
for result_criteria in result_criteria_list:
  trans_result = chain.invoke(
    {"text": result_criteria['reasoning']},
    config={"callbacks": [ollma_callback]}
  )
  trans_result_list.append(trans_result)
meta_map["llm_call3-04"] = ollma_callback
for i in range(len(result_criteria_list)):
  result_temp = [result_criteria_list[i]['score'],result_criteria_list[i]['value'],trans_result_list[i]]
  map_key = f"result0{i+2}"
  result_map[map_key] = result_temp
# ============================================================
# Step 4: 評価結果の出力とトークン量の確認
# ============================================================
## LLMトークン量確認
common_func.token_check(meta_map)
# 出力結果をDataFrameにまとめる
df = pd.DataFrame.from_dict(
    result_map,
    orient='index',
    columns=['score', 'value', 'reasoning']
).reset_index().rename(columns={'index': 'result_id'})
label_map = {
    'result01': 'reference評価',
    'result02': 'criteria評価（簡潔さ）',
    'result03': 'criteria評価（完全性）',
}
df['evaluation_label'] = df['result_id'].map(label_map)
# サマリーを出力
md_text = print_evaluation_report_markdown(df)
common_func.res_output_md(response=md_text,file_name=f"test04-assesment_summary")