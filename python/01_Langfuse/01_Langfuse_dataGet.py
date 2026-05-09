import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
# clickhouse
import clickhouse_connect
client = clickhouse_connect.get_client(
  host='localhost',
  port=8123,
  username=os.environ["CH_USER"],
  password=os.environ["CH_PASSWORD"],
  database=os.environ["CH_DB"]
)
# クエリ結果を直接DataFrameで取得
## タグ、日別、モデル別SQL
df = client.query_df("""
SELECT
  toDate(observations.start_time) AS date,
  observations.provided_model_name AS model,
  traces.tags,
  SUM(observations.usage_details['input']) AS input_tokens,
  SUM(observations.usage_details['output']) AS output_tokens,
  SUM(observations.total_cost) AS cost_usd
FROM observations FINAL
INNER JOIN traces FINAL ON observations.trace_id = traces.id
WHERE
  observations.type = 'GENERATION'
  AND observations.start_time >= '2025-01-01'
GROUP BY date, model, traces.tags
ORDER BY date DESC, cost_usd DESC
""")
print(df)