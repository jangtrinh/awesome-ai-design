"""Weekly freshness check. Updates link_status, stars, last_push, archived and last_checked in data/tools.yaml.
Needs GH_TOKEN for the GitHub API. Prints a report; does not delete entries (a person decides)."""
import datetime, json, os, pathlib, subprocess, urllib.request, yaml
ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT / "data/tools.yaml"
data = yaml.safe_load(path.read_text())
today = datetime.date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0 awesome-ai-design link check"}
report = []
for t in data["tools"]:
    try:
        with urllib.request.urlopen(urllib.request.Request(t["url"], headers=UA), timeout=25) as r: status = r.status
    except urllib.error.HTTPError as e: status = e.code
    except Exception: status = 0
    if t.get("repo"):
        hdr = dict(UA)
        if os.environ.get("GH_TOKEN"): hdr["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
        req = urllib.request.Request(f"https://api.github.com/repos/{t['repo']}", headers=hdr)
        try:
            j = json.load(urllib.request.urlopen(req, timeout=25))
            t["stars"], t["last_push"], t["archived"] = j["stargazers_count"], j["pushed_at"][:10], j["archived"]
        except Exception as e: report.append(f"{t['slug']}: GitHub API error {e}")
    if status != t["link_status"]: report.append(f"{t['slug']}: link {t['link_status']} -> {status}")
    t["link_status"] = status if status else t["link_status"]
    if status == 200: t["last_checked"] = today
    if t.get("archived"): report.append(f"{t['slug']}: archived, remove or move")
    if t.get("last_push") and (datetime.date.today() - datetime.date.fromisoformat(t["last_push"])).days > 183: report.append(f"{t['slug']}: no push for 6+ months")
path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=200))
print("\n".join(report) or "all entries healthy")
