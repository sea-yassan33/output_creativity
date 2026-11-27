import sys
sys.dont_write_bytecode = True
import pandas as pd
SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
SEVERITY_EMOJI = {
  "CRITICAL": "🔴 CRITICAL",
  "HIGH":     "🟠 HIGH",
  "MEDIUM":   "🟡 MEDIUM",
  "LOW":      "🟢 LOW",
  "UNKNOWN":  "⚪ UNKNOWN",
}
def extract_fixed_version(affected):
  for af in affected:
    for rng in af.get("ranges", []):
      for event in rng.get("events", []):
        if "fixed" in event:
          return event["fixed"]
  return "—（修正版なし）"
def extract_introduced_version(affected):
  for af in affected:
    for rng in af.get("ranges", []):
      for event in rng.get("events", []):
        if "introduced" in event:
          return event["introduced"]
  return "不明"
def build_urls(vuln_id, aliases):
  urls = {}
  ghsa = next((a for a in aliases if a.startswith("GHSA-")), None)
  cve  = vuln_id if vuln_id.startswith("CVE-") else next((a for a in aliases if a.startswith("CVE-")), None)
  if cve:
    urls["NVD"]         = f"https://nvd.nist.gov/vuln/detail/{cve}"
    urls["CVE_Details"] = f"https://www.cvedetails.com/cve/{cve}/"
  if ghsa:
    urls["GitHub_Advisory"] = f"https://github.com/advisories/{ghsa}"
  urls["OSV"] = f"https://osv.dev/vulnerability/{vuln_id}"
  return urls
def build_commands(pkg_name, fixed_ver):
  if fixed_ver == "—（修正版なし）":
    update_cmd = f"# 修正バージョンなし。代替パッケージを検討"
    overrides  = f'"overrides": {{ "{pkg_name}": "latest" }}'
  else:
    update_cmd = f"npm install {pkg_name}@{fixed_ver}"
    overrides  = f'"overrides": {{ "{pkg_name}": "{fixed_ver}" }}'
  return {
    "CMD_依存ツリー":   f"npm ls {pkg_name}",
    "CMD_利用箇所検索": f"grep -rn \"{pkg_name}\" ./src --include='*.ts' --include='*.tsx'",
    "CMD_アップデート": update_cmd,
    "CMD_overrides":    overrides,
  }
def build_commands_py(pkg_name, fixed_ver):
  if fixed_ver == "—（修正版なし）":
    update_cmd = f"# 修正バージョンなし。代替パッケージを検討"
    overrides  = f'"overrides": {{ "{pkg_name}": "latest" }}'
  else:
    update_cmd = f"pip install \"{pkg_name}=={fixed_ver}\""
    overrides  = f'"overrides": {{ "{pkg_name}": "{fixed_ver}" }}'
  return {
    "CMD_依存ツリー":   f"pip show {pkg_name}",
    "CMD_利用箇所検索": f"grep -rn \"{pkg_name}\" ./src",
    "CMD_アップデート": update_cmd,
    "CMD_overrides":    overrides,
  }
def parse_osv_json(data, min_severity="UNKNOWN",pl="node"):
  min_rank = SEVERITY_ORDER.get(min_severity.upper(), 3)
  rows = []
  for result in data.get("results", []):
    source_path = result.get("source", {}).get("path", "不明")
    for pkg_entry in result.get("packages", []):
      pkg       = pkg_entry.get("package", {})
      pkg_name  = pkg.get("name", "不明")
      pkg_ver   = pkg.get("version", "不明")
      ecosystem = pkg.get("ecosystem", "不明")
      for vuln in pkg_entry.get("vulnerabilities", []):
        vuln_id  = vuln.get("id", "不明")
        aliases  = vuln.get("aliases", [])
        summary  = vuln.get("summary", "—")
        severity = vuln.get("database_specific", {}).get("severity", "UNKNOWN").upper()
        if SEVERITY_ORDER.get(severity, 0) < min_rank:
          continue
        affected       = vuln.get("affected", [])
        fixed_ver      = extract_fixed_version(affected)
        introduced_ver = extract_introduced_version(affected)
        urls           = build_urls(vuln_id, aliases)
        if pl=="node":
          commands       = build_commands(pkg_name, fixed_ver)
        else:
          commands       = build_commands_py(pkg_name, fixed_ver)
        cve  = vuln_id if vuln_id.startswith("CVE-") else next((a for a in aliases if a.startswith("CVE-")), "—")
        rows.append({
          "Severity":           SEVERITY_EMOJI.get(severity, severity),
          "CVE_ID":             cve,
          "概要":               summary,
          "パッケージ名":       pkg_name,
          "現在バージョン":     pkg_ver,
          "影響開始バージョン": introduced_ver,
          "修正バージョン":     fixed_ver,
          "Ecosystem":          ecosystem,
          "ロックファイル":     source_path,
          "URL_NVD":            urls.get("NVD", "—"),
          "URL_OSV":            urls.get("OSV", "—"),
          "URL_GitHub_Advisory":urls.get("GitHub_Advisory", "—"),
          "URL_CVE_Details":    urls.get("CVE_Details", "—"),
          **commands,
        })
  if not rows:
    print(f"✅ {min_severity.upper()} 以上の脆弱性は検出されませんでした。")
    return pd.DataFrame()
  df = pd.DataFrame(rows)
  df["_sort"] = df["Severity"].apply(lambda s: SEVERITY_ORDER.get(next((k for k in SEVERITY_ORDER if k in s.upper()), "UNKNOWN"), 0))
  df = df.sort_values("_sort", ascending=False).drop(columns=["_sort"]).reset_index(drop=True)
  df.index += 1
  return df