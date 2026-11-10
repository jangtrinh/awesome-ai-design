"""Turn a GitHub issue-form body into a new data/tools.yaml entry."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from urllib.parse import urlsplit

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "data/schema/tool.schema.json").read_text())
JOBS = list(SCHEMA["properties"]["job"]["enum"])
PRICE_MODELS = [p for p in SCHEMA["properties"]["price_model"]["enum"] if p != "unverified"]
KINDS = ["app", "mcp-server", "agent-skill", "library", "plugin", "cli", "model", "spec", "other"]
RUNS = ["cloud", "local", "cloud or local", "in design app", "n/a"]
AFFILIATIONS = ["no", "yes, I made it or work on it", "yes, I am paid by it"]
MCP_ANSWERS = ["yes", "no", "not sure"]
SHARED_HOSTS = {
    "github.com",
    "gitlab.com",
    "codeberg.org",
    "bitbucket.org",
    "huggingface.co",
    "npmjs.com",
    "pypi.org",
    "figma.com",
    "chromewebstore.google.com",
    "marketplace.visualstudio.com",
    "apps.apple.com",
    "play.google.com",
    "youtube.com",
    "medium.com",
    "dev.to",
    "vercel.app",
    "netlify.app",
    "github.io",
}
_FORGE_HOSTS = {"github.com", "gitlab.com", "codeberg.org"}
_OS_LICENCES = {
    "mit",
    "apache-2.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "isc",
    "mpl-2.0",
    "gpl-2.0",
    "gpl-3.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "agpl-3.0",
    "unlicense",
    "0bsd",
    "zlib",
    "epl-2.0",
}
for _base in ("gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0"):
    _OS_LICENCES.add(f"{_base}-only")
    _OS_LICENCES.add(f"{_base}-or-later")
_SA_NEEDLES = (
    "polyform",
    "busl",
    "bsl-1.1",
    "business source",
    "elastic",
    "sspl",
    "commons clause",
    "fair source",
    "fsl-",
)
_LABELS = {
    "Name": "name",
    "URL (repo or product page)": "url",
    "Job it does": "job",
    "Kind": "kind",
    "Where it runs": "runs",
    "Price model": "price",
    "Licence (SPDX id, or licence name if source-available or proprietary)": "licence",
    "Is it or does it ship an MCP server?": "mcp",
    "One factual sentence on what it does (max 220 characters, no marketing words)": "description",
    "Are you affiliated with this project?": "affiliation",
    "Checks": "checks",
}
_REQUIRED = (
    ("name", "Name"),
    ("url", "URL"),
    ("job", "Job it does"),
    ("kind", "Kind"),
    ("runs", "Where it runs"),
    ("price", "Price model"),
    ("licence", "Licence"),
    ("description", "Description"),
    ("affiliation", "Affiliation"),
)
_MARKUP = frozenset("<>`[]()")
_CHECK_PREFIX = "It helps AI do real design work"
_CHECKED = re.compile(r"^-\s+\[([Xx])\]\s+(.*)$")
_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_UA = "Mozilla/5.0 awesome-ai-design add-tool bot"
_MARKER = "<!-- add-tool-bot -->"
_ENTRY_KEYS = (
    "slug",
    "name",
    "url",
    "job",
    "kind",
    "mcp_server",
    "runs",
    "price_model",
    "price_checked",
    "licence",
    "licence_class",
    "agents_named_in_docs",
    "repo",
    "stars",
    "last_push",
    "archived",
    "link_status",
    "last_checked",
    "maintainer_entry",
    "tested_by_maintainer",
    "description",
)


def parse_issue_form(body: str) -> dict:
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    out: dict = {}
    for part in re.split(r"(?m)^### ", text)[1:]:
        heading, _, rest = part.partition("\n")
        key = _LABELS.get(heading.strip())
        if not key:
            continue
        raw = rest.strip()
        if key == "checks":
            if not raw or raw == "_No response_":
                out[key] = None
                continue
            found = []
            for line in rest.splitlines():
                m = _CHECKED.match(line.strip())
                if m:
                    found.append(m.group(2).strip())
            out[key] = found
            continue
        if not raw or raw == "_No response_":
            out[key] = None
        else:
            out[key] = re.sub(r"\n+", " ", raw).strip()
    return out


def normalize_url(url) -> str | None:
    if url is None:
        return None
    url = str(url).strip()
    if not url:
        return None
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        return None
    host = parts.hostname
    if not host:
        return None
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return None
    try:
        port = parts.port
    except ValueError:
        return None
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    else:
        netloc = host
    path = (parts.path or "").rstrip("/")
    if path.endswith(".git"):
        path = path[:-4].rstrip("/")
    segs = [s for s in path.split("/") if s]
    if host in _FORGE_HOSTS:
        segs = [s.lower() for s in segs[:2]]
    return netloc + ("/" + "/".join(segs) if segs else "")


def _host_of(norm: str | None) -> str | None:
    if not norm:
        return None
    return norm.split("/", 1)[0]


def is_shared_host(host: str) -> bool:
    host = host.lower()
    return any(host == h or host.endswith("." + h) for h in SHARED_HOSTS)


def find_duplicate(name, url, tools, allow_same_domain=False):
    norm = normalize_url(url)
    incoming_name = (name or "").casefold().strip()
    incoming_host = _host_of(norm)
    for tool in tools:
        existing_norm = normalize_url(tool.get("url"))
        if norm and existing_norm and norm == existing_norm:
            return tool, "same URL"
        repo = tool.get("repo")
        if norm and repo and norm == "github.com/" + str(repo).lower():
            return tool, "same URL"
    for tool in tools:
        if incoming_name and incoming_name == str(tool.get("name", "")).casefold().strip():
            return tool, "same name"
    if allow_same_domain or not incoming_host or is_shared_host(incoming_host):
        return None
    for tool in tools:
        existing_host = _host_of(normalize_url(tool.get("url")))
        if existing_host and incoming_host == existing_host:
            return tool, f"same site ({incoming_host})"
    return None


def _has_markup(text: str) -> bool:
    return any(c in text for c in _MARKUP) or "http://" in text or "https://" in text


def validate_form(form: dict) -> list[str]:
    errors = []
    for key, label in _REQUIRED:
        if not form.get(key):
            errors.append(f"{label} is required.")
    name = form.get("name")
    if name:
        if len(name) > 80:
            errors.append("Name must be at most 80 characters.")
        if _has_markup(name):
            errors.append("Name must not contain links or markup.")
    url = form.get("url")
    if url and normalize_url(url) is None:
        errors.append("URL must be an http or https link.")
    job = form.get("job")
    if job and job not in JOBS:
        errors.append("Job must be one of: " + ", ".join(JOBS) + ".")
    kind = form.get("kind")
    if kind and kind not in KINDS:
        errors.append("Kind must be one of: " + ", ".join(KINDS) + ".")
    runs = form.get("runs")
    if runs and runs not in RUNS:
        errors.append("Where it runs must be one of: " + ", ".join(RUNS) + ".")
    price = form.get("price")
    if price and price not in PRICE_MODELS:
        errors.append("Price model must be one of: " + ", ".join(PRICE_MODELS) + ".")
    licence = form.get("licence")
    if licence:
        if len(licence) > 80:
            errors.append("Licence must be at most 80 characters.")
        if any(c in licence for c in "<>`[]") or "http://" in licence or "https://" in licence:
            errors.append("Licence must not contain links or markup.")
    affiliation = form.get("affiliation")
    if affiliation and affiliation not in AFFILIATIONS:
        errors.append("Affiliation must be one of: " + "; ".join(AFFILIATIONS) + ".")
    mcp = form.get("mcp")
    if mcp and mcp not in MCP_ANSWERS:
        errors.append("MCP server answer must be one of: " + ", ".join(MCP_ANSWERS) + ".")
    description = form.get("description")
    if description:
        if len(description) > 220:
            errors.append("Description must be at most 220 characters.")
        if _has_markup(description):
            errors.append("Description must not contain links or markup.")
    checks = form.get("checks") or []
    if not any(c.startswith(_CHECK_PREFIX) for c in checks):
        errors.append(f'Tick the box that starts with "{_CHECK_PREFIX}".')
    return errors


def slugify(name, existing_slugs) -> str:
    existing = set(existing_slugs)
    folded = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")[:60].strip("-")
    if not _SLUG_RE.fullmatch(slug or ""):
        slug = "tool"
    if slug not in existing:
        return slug
    n = 2
    while True:
        suffix = f"-{n}"
        base = slug[: 60 - len(suffix)].rstrip("-") or "tool"
        cand = f"{base}{suffix}"
        if not _SLUG_RE.fullmatch(cand):
            cand = f"tool-{n}"
        if cand not in existing:
            return cand
        n += 1


def licence_class_for(licence) -> str:
    key = (licence or "").strip().casefold()
    if key in _OS_LICENCES:
        return "open-source"
    if "proprietary" in key:
        return "proprietary"
    if any(n in key for n in _SA_NEEDLES):
        return "source-available"
    return "unclear"


def _github_repo(url: str) -> str | None:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "github.com":
        return None
    segs = [s for s in (parts.path or "").split("/") if s]
    if len(segs) < 2:
        return None
    owner, repo = segs[0], segs[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"


def build_entry(form, existing_slugs, today: str, link_status: int) -> dict:
    url = form["url"].strip()
    mcp = (form.get("mcp") or "").strip().casefold()
    entry = {
        "slug": slugify(form["name"], existing_slugs),
        "name": form["name"].strip(),
        "url": url,
        "job": form["job"],
        "kind": form["kind"],
        "mcp_server": "mentioned-on-page" if mcp == "yes" else "no-evidence",
        "runs": form["runs"],
        "price_model": form["price"],
        "price_checked": False,
        "licence": form["licence"],
        "licence_class": licence_class_for(form["licence"]),
        "agents_named_in_docs": [],
        "repo": _github_repo(url),
        "stars": None,
        "last_push": None,
        "archived": None,
        "link_status": link_status,
        "last_checked": today,
        "maintainer_entry": False,
        "tested_by_maintainer": "unconfirmed",
        "description": form["description"].rstrip(" "),
    }
    jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker()).validate(entry)
    return entry


def insert_entry(tools, entry, job_order) -> list:
    job = entry["job"]
    last_same = None
    for i, t in enumerate(tools):
        if t.get("job") == job:
            last_same = i
    if last_same is not None:
        i = last_same + 1
        return tools[:i] + [entry] + tools[i:]
    rank = {j: n for n, j in enumerate(job_order)}
    my = rank.get(job, len(job_order))
    for i, t in enumerate(tools):
        if rank.get(t.get("job"), len(job_order)) > my:
            return tools[:i] + [entry] + tools[i:]
    return tools + [entry]


def check_link(url, timeout=20) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def dump_yaml(data) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=200)


def _branch(issue: int, slug: str) -> str:
    existing = os.environ.get("EXISTING_BRANCH") or ""
    if re.fullmatch(rf"add-tool/{issue}-[a-z0-9-]+", existing):
        return existing
    return f"add-tool/{issue}-{slug}"


def _table(rows: list[tuple[str, object]]) -> str:
    lines = ["| Field | Value |", "| --- | --- |"]
    for k, v in rows:
        val = "" if v is None else str(v).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {k} | {val} |")
    return "\n".join(lines)


def _pr_body(issue: int, form: dict, entry: dict | None, notes: list[str]) -> str:
    if entry:
        rows = [(k, entry.get(k)) for k in _ENTRY_KEYS]
    else:
        rows = [(k, form.get(k)) for k in ("name", "url", "job", "kind", "runs", "price", "licence", "mcp", "description")]
    parts = [
        "Proposed entry:",
        "",
        _table(rows),
        "",
        f"Affiliation: {form.get('affiliation') or ''}",
        "",
    ]
    if notes:
        parts += ["Notes:", ""] + [f"- {n}" for n in notes] + [""]
    parts += [
        "Maintainer checklist:",
        "",
        "- [ ] Verify price and licence",
        "- [ ] Check the description is factual",
        "- [ ] Confirm it belongs on the list",
        "",
        f"Closes #{issue}",
        "",
        "CI runs when the maintainer marks the draft ready for review.",
        "",
    ]
    return "\n".join(parts)


def _invalid_comment(errors: list[str]) -> str:
    lines = [_MARKER, "This submission could not be added:", ""]
    lines += [f"- {e}" for e in errors]
    lines += ["", "Edit the issue to fix these problems. The bot runs again when the issue is edited.", ""]
    return "\n".join(lines)


def _dup_comment(tool: dict, reason: str) -> str:
    return (
        f"{_MARKER}\n"
        f"This looks like a duplicate of {tool['name']} ({tool['url']}): {reason}.\n"
        "\n"
        "If this is a different product on the same site, a maintainer can add the `not-duplicate` label.\n"
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Add a tool from a GitHub issue form.")
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-network", action="store_true")
    p.add_argument("--allow-same-domain", action="store_true")
    p.add_argument("--today", default=None)
    args = p.parse_args(argv)
    if "ISSUE_BODY" not in os.environ:
        raise RuntimeError("ISSUE_BODY is not set")
    form = parse_issue_form(os.environ["ISSUE_BODY"])
    today = args.today or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    yaml_path = pathlib.Path(args.root) / "data" / "tools.yaml"
    data = yaml.safe_load(yaml_path.read_text())
    tools = data["tools"]
    slugs = [t["slug"] for t in tools]
    slug = slugify(form.get("name") or "tool", slugs)
    name = form.get("name")
    job = form.get("job")
    notes: list[str] = []
    errors = validate_form(form)
    status = "ok"
    comment = None
    duplicate_of = None
    entry = None

    if errors:
        status = "invalid"
        comment = _invalid_comment(errors)
    else:
        hit = find_duplicate(name, form.get("url"), tools, allow_same_domain=args.allow_same_domain)
        if hit:
            tool, reason = hit
            status = "duplicate"
            duplicate_of = {"slug": tool["slug"], "name": tool["name"], "url": tool["url"], "reason": reason}
            comment = _dup_comment(tool, reason)
        else:
            if args.no_network:
                link_status = 200
            else:
                link_status = check_link(form["url"])
            if link_status in (401, 403, 429):
                notes.append(
                    f"link returned HTTP {link_status} to the bot (bot protection?); check by hand"
                )
                link_status = 200
            if link_status != 200:
                status = "invalid"
                errors = [
                    f"The URL returned HTTP {link_status} (0 = no response). Use a link that loads."
                ]
                comment = _invalid_comment(errors)
            else:
                entry = build_entry(form, slugs, today, link_status)
                slug = entry["slug"]
                name = entry["name"]
                job = entry["job"]
                data["tools"] = insert_entry(tools, entry, JOBS)
                yaml_path.write_text(dump_yaml(data))

    result = {
        "status": status,
        "errors": errors,
        "notes": notes,
        "slug": slug,
        "name": name,
        "job": job,
        "branch": _branch(args.issue, slug),
        "pr_title": f"Add {name}" if name else "Add tool",
        "pr_body": _pr_body(args.issue, form, entry, notes),
        "labels": ["new-tool", f"job:{job or ''}"],
        "duplicate_of": duplicate_of,
        "comment": comment,
    }
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
