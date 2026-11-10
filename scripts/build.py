"""Build README.md, data/tools.json, llms.txt and llms-full.txt from data/tools.yaml.
data/tools.yaml is the only file people edit. Everything else is generated."""
import json, sys, pathlib, yaml, jsonschema
ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/jangtrinh/awesome-ai-design"
data = yaml.safe_load((ROOT/"data/tools.yaml").read_text())
tools = data["tools"]
schema = json.loads((ROOT/"data/schema/tool.schema.json").read_text())
JOBS = [
 ("generate-ui","Generate UI from a prompt","Prompt, sketch or screenshot in; screens, prototypes or running apps out."),
 ("design-with-agents","Design with an agent on the canvas","Design editors where a person and an agent work on the same file."),
 ("connect-agents-to-design-files","Connect agents to design files","MCP servers and bridges that let Claude Code, Codex, Cursor and other agents read and write design files."),
 ("teach-agents-taste","Teach agents taste","Skills, specs and guidelines that change what an agent designs, not only how fast."),
 ("stay-on-system","Keep output on your design system","Components, tokens and docs that keep generated UI on-brand."),
 ("design-to-code","Turn designs into code","Convert a finished design into production front-end code."),
 ("make-3d","Make 3D with agents","Generate, edit and check 3D assets with models and agents."),
 ("make-vectors-and-motion","Make vectors and motion","Vector generation, vectorising and agent-driven animation."),
 ("check-what-agents-built","Check what agents built","Screenshots, accessibility checks and user flows, so an agent can verify its own output."),
]
# ---- rules encoded in structure ----
errors = []
seen = set()
for t in tools:
    try: jsonschema.validate(t, schema)
    except jsonschema.ValidationError as e: errors.append(f"{t.get('slug')}: {e.message}")
    if t["slug"] in seen: errors.append(f"duplicate slug {t['slug']}")
    seen.add(t["slug"])
    if t["archived"]: errors.append(f"{t['slug']}: archived repos are not listed")
    if t["link_status"] != 200: errors.append(f"{t['slug']}: link status {t['link_status']}")
    if t["maintainer_entry"]:
        if "figma" in t["name"].lower(): errors.append(f"{t['slug']}: maintainer product names must not contain Figma")
        if t["licence_class"] != "source-available": errors.append(f"{t['slug']}: maintainer entries are source-available")
        if "open source" in t["description"].lower() or "open-source" in t["description"].lower(): errors.append(f"{t['slug']}: never call a maintainer entry open source")
for job, _, _ in JOBS:
    n = sum(1 for t in tools if t["job"] == job and t["maintainer_entry"])
    if n > 1: errors.append(f"{job}: {n} maintainer entries (max 1)")
if errors:
    print("\n".join(errors)); sys.exit(1)
by = {t["slug"]: t for t in tools}
def table(head, rows):
    w = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
    fmt = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return [fmt(head), "| " + " | ".join("-" * w[i] for i in range(len(w))) + " |"] + [fmt(r) for r in rows]

def k(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)
PRICE = {"free":"Free","freemium":"Freemium","paid":"Paid","paid-for-full-access":"Paid plan for full access","free-for-individuals":"Free for individuals","unverified":"Price unverified"}
def tags(t):
    p = "FREE" if t["maintainer_entry"] else PRICE[t["price_model"]]
    lic = {"open-source":f"open source ({t['licence']})","source-available":"source-available (PolyForm Shield)" if t["maintainer_entry"] else f"source-available ({t['licence']})","proprietary":"proprietary","mixed":"licence varies","unclear":"licence unclear"}[t["licence_class"]]
    out = [p, lic, t["runs"]]
    if t["mcp_server"] == "yes": out.append("MCP")
    if t["stars"] is not None: out.append(f"{k(t['stars'])} stars")
    out.append(f"checked {t['last_checked']}")
    return " · ".join(out)
def line(t):
    d = t["description"].rstrip(".") + "."
    if t["maintainer_entry"]: d += " Disclosure: made by the maintainer of this list."
    return f"- [{t['name']}]({t['url']}) - {d} `{tags(t)}`."
QUICK = [
 ("Product designer trying AI agents", ["google-stitch","penpot-mcp-server","ui-ux-pro-max"]),
 ("Design engineer wiring agents to design files", ["figma-mcp-server-official","shadcn-ui-mcp-server","playwright-mcp"]),
 ("Indie maker working in 3D or motion", ["mcp-for-blender","trellis-2","remotion-agent-skills"]),
]
RECIPES = [
 ("prompt-to-verified-react-screen","Prompt to an on-brand React screen, checked by the agent",
  [("design-md","Describe the brand in one file the agent reads first."),("ui-ux-pro-max","Give the agent style, palette and UX rules."),("shadcn-ui-mcp-server","Let it install real components instead of inventing them."),("playwright-mcp","Have it screenshot the result and compare against the brief."),("axe-core","Run accessibility checks before you review.")]),
 ("design-file-to-production-code","Design file to production code that reuses your components",
  [("figma-mcp-server-official","Give the agent the frame, variables and Code Connect data."),("storybook-mcp","Point it at your existing components and docs."),("chrome-devtools-mcp","Let it debug layout against the running app.")]),
 ("agent-built-3d-part","Agent-built 3D asset or printable part",
  [("trellis-2","Start from a reference image when you have one."),("mcp-for-blender","Let the agent refine the mesh, materials and render in Blender."),("playwright-mcp","Not needed here; check renders by eye or with Blender's own render output.")]),
 ("svg-to-motion","Vector illustration to a rendered motion clip",
  [("recraft","Generate an editable vector illustration."),("vtracer","Or vectorise a raster image you already have."),("remotion-agent-skills","Teach the agent Remotion, then have it animate and render the clip.")]),
]
# drop the weak step in recipe 3 (kept honest: no fake step)
RECIPES[2] = (RECIPES[2][0], RECIPES[2][1], RECIPES[2][2][:2])
L = []
L.append("# Awesome AI Design [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)\n")
L.append("> Tools, MCP servers and agent skills that let AI take part in interface, 3D and motion design.\n")
L.append(f"{len(tools)} entries, organised by the job you are doing. Each entry carries its price model, licence, where it runs, whether it is an MCP server, and the date its link was last checked. The same data is in [`data/tools.json`](data/tools.json) for scripts and agents, with a summary in [`llms.txt`](llms.txt).\n")
L.append("## Contents\n")
L.append("- [Start here](#start-here)")
for job, title, _ in JOBS: L.append(f"- [{title}](#{title.lower().replace(' ','-')})")
L.append("- [Compare: agent access to design files](#compare-agent-access-to-design-files)")
L.append("- [Stack recipes](#stack-recipes)")
L.append("- [Related lists](#related-lists)\n")
L.append("## Start here\n")
L.append("Three picks per reader, all listed below. Maintainer-made tools are never in this section.\n")
L += table(["Reader", "Start with"], [[who, ", ".join(by[x]["name"] for x in slugs)] for who, slugs in QUICK])
L.append("\nTags read `price · licence · where it runs · MCP · stars · last checked`.\n")
for job, title, intro in JOBS:
    L.append(f"## {title}\n\n{intro}\n")
    for t in [t for t in tools if t["job"] == job]: L.append(line(t))
    L.append("")
L.append("## Compare: agent access to design files\n")
def lic_short(t):
    return "source-available (PolyForm Shield)" if t["maintainer_entry"] else t["licence"]
L += table(["Tool", "Type", "Runs", "Price", "Licence"], [[t["name"], t["kind"], t["runs"], "FREE" if t["maintainer_entry"] else PRICE[t["price_model"]], lic_short(t)] for t in tools if t["job"] == "connect-agents-to-design-files"])
L.append("")
L.append("## Stack recipes\n")
L.append("Each recipe only uses tools listed above. Steps are a starting point, not a benchmark.\n")
for rid, title, steps in RECIPES:
    L.append(f"### {title}\n")
    L += table(["Step", "Tool", "What it does here"], [[str(i), by[x]["name"], why] for i, (x, why) in enumerate(steps, 1)])
    L.append("")
L.append("## Related lists\n")
for n,u,d in [("AI Tools for UI","https://github.com/maxbogo/awesome-ai-tools-for-ui#readme","Skills, apps and MCP servers for building UI with AI."),("AI Design Workflows","https://github.com/humbleteam/awesome-ai-design-workflows#readme","Standards and patterns for product teams using AI."),("Generative UI","https://github.com/narrowin/awesome-generative-ui#readme","Interfaces that a model renders at runtime."),("Motion Design Agent Skills","https://github.com/frankxai/awesome-motion-design-agent-skills#readme","Agent skills for web animation and video."),("Blender","https://github.com/agmmnn/awesome-blender#readme","Add-ons, tools and resources for the open-source 3D suite."),("MCP Servers","https://github.com/punkpeye/awesome-mcp-servers#readme","Model Context Protocol servers of every kind."),("DESIGN.md","https://github.com/VoltAgent/awesome-design-md#readme","Brand design systems written for agents.")]:
    L.append(f"- [{n}]({u}) - {d}")
L.append("\n## Footnotes\n")
L.append("Read the [contribution guidelines](contributing.md) before adding a tool; edit `data/tools.yaml`, not this file. Entries marked \"Disclosure: made by the maintainer of this list\" meet the same criteria as every other entry, there is at most one per section, and they never appear in Start here. Links are checked every week by `scripts/check_links.py`.\n")
(ROOT/"README.md").write_text("\n".join(L) + "\n")
# ---- machine outputs ----
(ROOT/"data/tools.json").write_text(json.dumps({"name":"Awesome AI Design","source":REPO,"licence":"CC0-1.0","count":len(tools),"jobs":[{"id":j,"title":t} for j,t,_ in JOBS],"tools":tools}, indent=1, ensure_ascii=False) + "\n")
def fact(t):
    lic = "source-available under PolyForm Shield" if t["maintainer_entry"] else {"open-source":f"open source under {t['licence']}","source-available":f"source-available under {t['licence']}","proprietary":"proprietary","mixed":"licensed per component","unclear":"of unclear licence"}[t["licence_class"]]
    price = "free" if t["maintainer_entry"] else ("of unverified price" if t["price_model"] == "unverified" else PRICE[t["price_model"]].lower())
    s = f"{t['name']} ({t['url']}): {t['description'].rstrip('.')}. It is {price} and {lic}. Runs: {t['runs']}."
    if t["mcp_server"] == "yes": s += " It is an MCP server or ships one."
    if t["agents_named_in_docs"]: s += " Its docs name " + ", ".join(t["agents_named_in_docs"]) + "."
    if t["maintainer_entry"]: s += " Made by the maintainer of Awesome AI Design."
    return s + f" Link checked {t['last_checked']}."
S = [f"# Awesome AI Design\n\n> Curated list of {len(tools)} tools, MCP servers and agent skills that let AI take part in interface, 3D and motion design, grouped by job, with price, licence, runtime and last-checked date for every entry.\n",
     f"- [Full list as JSON]({REPO}/blob/main/data/tools.json): every entry with all fields",
     f"- [Full text for models]({REPO}/blob/main/llms-full.txt): one self-contained sentence per tool",
     f"- [Agent instructions]({REPO}/blob/main/AGENTS.md): how a coding agent should pick a tool from this list\n", "## Jobs\n"]
for j,title,intro in JOBS: S.append(f"- [{title}]({REPO}#{title.lower().replace(' ','-')}): {intro}")
(ROOT/"llms.txt").write_text("\n".join(S) + "\n")
F = [f"# Awesome AI Design: full text\n\nSource: {REPO} (CC0-1.0). {len(tools)} entries. Each line stands alone and can be quoted.\n"]
for j,title,intro in JOBS:
    F.append(f"## {title}\n\n{intro}\n")
    F += [fact(t) + "\n" for t in tools if t["job"] == j]
(ROOT/"llms-full.txt").write_text("\n".join(F))
print(f"ok: {len(tools)} tools, README + tools.json + llms.txt + llms-full.txt written")
