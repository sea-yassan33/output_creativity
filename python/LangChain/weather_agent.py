import warnings
# 警告を非表示にする
warnings.filterwarnings('ignore')
## === ライブラリ ===
import os
from dotenv import load_dotenv
load_dotenv()
from geopy.geocoders import Nominatim
import requests
## LangChain系ライブラリ
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor,create_tool_calling_agent
from langchain_classic.agents.format_scratchpad.tools import format_to_tool_messages
from langchain_classic.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
## model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.environ['GOOGLE_AI_ST_API'], temperature=0.5)
## === 関数 ===
## 天気予報ajentツール
@tool
def get_weekly_forecast(location: str):
  """
  指定された地名の1週間の天気予報を取得するツール。
  location: 地名（例: '東京都', 'Osaka'）
  """
  WEATHER_CODE_MAP = {0: "快晴", 1: "晴れ", 2: "薄曇り", 3: "曇り", 45: "霧", 48: "霧氷", 51: "霧雨", 53: "霧雨", 55: "霧雨", 61: "小雨", 63: "雨", 65: "強い雨", 71: "小雪", 73: "雪", 75: "強い雪", 80: "にわか雨", 81: "雨", 82: "激しいにわか雨", 85: "にわか雪", 86: "大雪"}
  geolocator = Nominatim(user_agent="test_weather_app")
  loc = geolocator.geocode(location)
  if loc is None:
    return {"error": "Location not found"} 
  params = {
    "latitude": loc.latitude,
    "longitude": loc.longitude,
    "hourly": ["temperature_2m", "weather_code"],
    "timezone": "Asia/Tokyo"
  }
  response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
  data = response.json()
  # データを整形
  times = data["hourly"]["time"]
  temps = data["hourly"]["temperature_2m"]
  codes = data["hourly"]["weather_code"]   
  time_interval = 6
  result = {}
  for i in range(0, len(times), time_interval):
    t = times[i]
    result[t] = {
      "temperature": temps[i],
      "weather": WEATHER_CODE_MAP.get(codes[i], f"不明({codes[i]})"),
    }
  return result
## レスポンス結果をマークダウンに変換
def convert_to_markdown(response):
  output_data = response["output"]
  markdown_content = ""
  if isinstance(output_data, list):
    # リスト内の各要素からテキストを抽出して結合
    parts = []
    for item in output_data:
      if isinstance(item, dict) and "text" in item:
        parts.append(item["text"])
      else:
        parts.append(str(item))
    markdown_content = "".join(parts)
  else:
    # すでに文字列の場合はそのまま
    markdown_content = str(output_data)
  return markdown_content
# === テンプレート作成 ===
prompt = ChatPromptTemplate.from_messages([
    ("system", """あなたは親切な気象アドバイザーです。
提供されたデータに基づき、以下の構成のMarkdown形式で回答してください。

# 1週間の天気予報
(ここに日ごとの天気を表形式で記載)

# 日常生活のアドバイス
(服装、洗濯、傘の必要性などを詳しく記載)

# ラッキーアイテム
(天気に合わせたアイテムを1つ提案)
"""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
# === エージェントの作成 ===
tools = [get_weekly_forecast]
agent = (
  {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
  }
  | prompt
  | model.bind_tools(tools)
  | ToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
## === 実行 ===
response = agent_executor.invoke({"input": "東京の１週間の天気予報をしてください。それに基づいた日常生活のアドバイスをお願いします。"})
## === 出力 ===
markdown_content =  convert_to_markdown(response)
if not os.path.exists("./out"):
  os.makedirs("./out")
with open(f"./out/res.md", "w", encoding="utf-8") as f:
  f.write(markdown_content)