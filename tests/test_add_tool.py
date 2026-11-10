import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.add_tool import (  # noqa: E402
    JOBS,
    build_entry,
    dump_yaml,
    find_duplicate,
    insert_entry,
    licence_class_for,
    main,
    normalize_url,
    parse_issue_form,
    slugify,
    validate_form,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
DATA = yaml.safe_load((ROOT / "data/tools.yaml").read_text())
TOOLS = DATA["tools"]
SCHEMA = json.loads((ROOT / "data/schema/tool.schema.json").read_text())
CHECK_PREFIX = "It helps AI do real design work"


def _body(name: str) -> str:
    return (FIXTURES / name).read_text()


def _form(name: str) -> dict:
    return parse_issue_form(_body(name))


def test_parse_valid():
    form = _form("issue_valid.md")
    assert form["name"] == "Acme Canvas MCP"
    assert form["url"] == "https://github.com/acme/canvas-mcp"
    assert form["job"] == "connect-agents-to-design-files"
    assert form["kind"] == "mcp-server"
    assert form["runs"] == "local"
    assert form["price"] == "free"
    assert form["licence"] == "MIT"
    assert form["mcp"] == "yes"
    assert form["description"].startswith("Local MCP server")
    assert form["affiliation"] == "no"
    assert form["checks"] == [
        "It helps AI do real design work (interface, visual, 3D, motion or UX), not a generic image generator or prompt pack"
    ]
    assert "extra" not in form


def test_parse_no_response_and_unchecked():
    form = _form("issue_invalid.md")
    assert form["job"] is None
    assert "https://" in form["description"]
    assert form["checks"] == []


def test_parse_checked_lowercase_x():
    form = _form("issue_dup_name.md")
    assert form["name"] == "playwright mcp"
    assert form["checks"] and form["checks"][0].startswith(CHECK_PREFIX)


def test_parse_crlf():
    raw = (FIXTURES / "issue_crlf.md").read_bytes()
    assert b"\r\n" in raw
    form = parse_issue_form(raw.decode())
    assert form["name"] == "Bolt Canvas"
    assert form["url"] == "https://boltcanvas.app"
    assert form["job"] == "generate-ui"
    assert form["kind"] == "app"
    assert form["runs"] == "cloud"
    assert form["affiliation"] == "no"
    assert form["checks"][0].startswith(CHECK_PREFIX)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("https://www.GitHub.com/penpot/penpot/", "github.com/penpot/penpot"),
        ("https://github.com/penpot/penpot.git", "github.com/penpot/penpot"),
        ("https://github.com/penpot/penpot?tab=readme-ov-file", "github.com/penpot/penpot"),
        ("https://github.com/penpot/penpot#readme", "github.com/penpot/penpot"),
        ("https://github.com/Penpot/Penpot/tree/develop/frontend", "github.com/penpot/penpot"),
        ("https://www.github.com/acme/canvas-mcp/", "github.com/acme/canvas-mcp"),
        ("http://example.com:80/foo", "example.com/foo"),
        ("https://example.com:443/bar/", "example.com/bar"),
        ("https://example.com:8080/x", "example.com:8080/x"),
        ("https://v0.app/", "v0.app"),
        ("https://v0.app/pricing", "v0.app/pricing"),
        ("https://www.example.com/path", "example.com/path"),
        ("https://gitlab.com/Group/Repo/extra", "gitlab.com/group/repo"),
        ("https://codeberg.org/Org/Proj.git", "codeberg.org/org/proj"),
        ("ftp://example.com/x", None),
        ("not-a-url", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_url(raw, expected):
    assert normalize_url(raw) == expected


def test_find_duplicate_url():
    hit = find_duplicate("Penpot Design", "https://www.GitHub.com/penpot/penpot/", TOOLS)
    assert hit is not None
    tool, reason = hit
    assert tool["slug"] == "penpot"
    assert reason == "same URL"


def test_find_duplicate_via_repo_field():
    tools = [
        {
            "slug": "docs-only",
            "name": "Docs Only",
            "url": "https://help.example.com/mcp",
            "repo": "acme/canvas-mcp",
        }
    ]
    hit = find_duplicate("Other", "https://github.com/ACME/canvas-mcp", tools)
    assert hit is not None
    tool, reason = hit
    assert tool["slug"] == "docs-only"
    assert reason == "same URL"


def test_find_duplicate_name():
    hit = find_duplicate("playwright mcp", "https://github.com/example/playwright-mcp-other", TOOLS)
    assert hit is not None
    tool, reason = hit
    assert tool["slug"] == "playwright-mcp"
    assert reason == "same name"


def test_find_duplicate_domain():
    hit = find_duplicate("V0 Pricing Page", "https://v0.app/pricing", TOOLS)
    assert hit is not None
    tool, reason = hit
    assert tool["slug"] == "v0"
    assert reason == "same site (v0.app)"


def test_find_duplicate_allow_same_domain():
    hit = find_duplicate(
        "V0 Pricing Page",
        "https://v0.app/pricing",
        TOOLS,
        allow_same_domain=True,
    )
    assert hit is None


def test_shared_hosts_are_not_domain_duplicates():
    hit = find_duplicate("Acme Canvas MCP", "https://github.com/acme/canvas-mcp", TOOLS)
    assert hit is None


def test_validate_form_ok():
    assert validate_form(_form("issue_valid.md")) == []


def test_validate_form_invalid_fixture():
    errors = validate_form(_form("issue_invalid.md"))
    joined = " ".join(errors)
    assert any("Job" in e for e in errors)
    assert any("Description" in e for e in errors)
    assert any(CHECK_PREFIX in e for e in errors)
    assert "required" in joined
    assert len(errors) >= 3


def test_validate_form_enums_and_limits():
    form = _form("issue_valid.md")
    form["job"] = "not-a-job"
    form["kind"] = "desktop-app"
    form["runs"] = "cloud or self-hosted"
    form["price"] = "unverified"
    form["name"] = "x" * 81
    form["description"] = "See https://example.com"
    errors = validate_form(form)
    joined = " ".join(errors)
    assert "Job must be" in joined
    assert "Kind must be" in joined
    assert "Where it runs must be" in joined
    assert "Price model must be" in joined
    assert "80" in joined
    assert "Description must not contain links or markup." in joined


def test_slugify_collision_and_unicode():
    assert slugify("Acme Canvas MCP", []) == "acme-canvas-mcp"
    assert slugify("Acme Canvas MCP", ["acme-canvas-mcp"]) == "acme-canvas-mcp-2"
    assert slugify("Acme Canvas MCP", ["acme-canvas-mcp", "acme-canvas-mcp-2"]) == "acme-canvas-mcp-3"
    assert slugify("Café UI", []) == "cafe-ui"
    assert slugify("你好", []) == "tool"
    assert slugify("???", ["tool"]) == "tool-2"
    assert slugify("Naïve Tool", []) == "naive-tool"


@pytest.mark.parametrize(
    "licence,expected",
    [
        ("MIT", "open-source"),
        ("mit", "open-source"),
        ("Apache-2.0", "open-source"),
        ("GPL-3.0-or-later", "open-source"),
        ("GPL-2.0-only", "open-source"),
        ("MPL-2.0", "open-source"),
        ("0BSD", "open-source"),
        ("proprietary (SaaS)", "proprietary"),
        ("Proprietary", "proprietary"),
        ("PolyForm-Shield-1.0.0 (read from LICENSE)", "source-available"),
        ("BUSL-1.1", "source-available"),
        ("Business Source License", "source-available"),
        ("SSPL-1.0", "source-available"),
        ("mystery", "unclear"),
        ("", "unclear"),
    ],
)
def test_licence_class_for(licence, expected):
    assert licence_class_for(licence) == expected


def test_insert_entry_end_of_job_group():
    tools = [
        {"job": "generate-ui", "slug": "a"},
        {"job": "generate-ui", "slug": "b"},
        {"job": "design-with-agents", "slug": "c"},
    ]
    out = insert_entry(tools, {"job": "generate-ui", "slug": "new"}, JOBS)
    assert [t["slug"] for t in out] == ["a", "b", "new", "c"]
    assert len(tools) == 3


def test_insert_entry_empty_job_group():
    tools = [
        {"job": "generate-ui", "slug": "a"},
        {"job": "design-to-code", "slug": "b"},
    ]
    out = insert_entry(tools, {"job": "design-with-agents", "slug": "new"}, JOBS)
    assert [t["slug"] for t in out] == ["a", "new", "b"]


def test_insert_entry_append_when_job_is_last():
    tools = [{"job": "generate-ui", "slug": "a"}]
    out = insert_entry(tools, {"job": "check-what-agents-built", "slug": "new"}, JOBS)
    assert [t["slug"] for t in out] == ["a", "new"]


def test_insert_entry_front_when_job_is_first_and_missing():
    tools = [{"job": "make-3d", "slug": "a"}]
    out = insert_entry(tools, {"job": "generate-ui", "slug": "new"}, JOBS)
    assert [t["slug"] for t in out] == ["new", "a"]


def test_build_entry_validates_against_schema():
    form = _form("issue_valid.md")
    slugs = [t["slug"] for t in TOOLS]
    entry = build_entry(form, slugs, "2026-11-10", 200)
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(entry)
    assert list(entry) == [
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
    ]
    assert entry["slug"] == "acme-canvas-mcp"
    assert entry["url"] == "https://github.com/acme/canvas-mcp"
    assert entry["mcp_server"] == "mentioned-on-page"
    assert entry["price_checked"] is False
    assert entry["licence_class"] == "open-source"
    assert entry["repo"] == "acme/canvas-mcp"
    assert entry["stars"] is None
    assert entry["maintainer_entry"] is False
    assert entry["tested_by_maintainer"] == "unconfirmed"
    assert entry["last_checked"] == "2026-11-10"
    assert entry["link_status"] == 200


def _prep_root(tmp_path: Path) -> Path:
    dest = tmp_path / "data"
    dest.mkdir()
    shutil.copy(ROOT / "data/tools.yaml", dest / "tools.yaml")
    schema = dest / "schema"
    schema.mkdir()
    shutil.copy(ROOT / "data/schema/tool.schema.json", schema / "tool.schema.json")
    return tmp_path


def _run(tmp_path: Path, monkeypatch, body: str, issue: int = 7, extra=None, env=None):
    root = _prep_root(tmp_path)
    monkeypatch.setenv("ISSUE_BODY", body)
    if env:
        for k, v in env.items():
            if v is None:
                monkeypatch.delenv(k, raising=False)
            else:
                monkeypatch.setenv(k, v)
    out = tmp_path / "result.json"
    argv = ["--root", str(root), "--issue", str(issue), "--out", str(out), "--no-network", "--today", "2026-11-10"]
    if extra:
        argv.extend(extra)
    code = main(argv)
    result = json.loads(out.read_text())
    yaml_path = root / "data" / "tools.yaml"
    return code, result, yaml_path


def test_main_ok_inserts_after_last_job_entry(tmp_path, monkeypatch):
    orig_tools = yaml.safe_load((ROOT / "data/tools.yaml").read_text())["tools"]
    last = max(i for i, t in enumerate(orig_tools) if t["job"] == "connect-agents-to-design-files")
    code, result, yaml_path = _run(tmp_path, monkeypatch, _body("issue_valid.md"))
    assert code == 0
    assert result["status"] == "ok"
    assert result["branch"] == "add-tool/7-acme-canvas-mcp"
    assert "Closes #7" in result["pr_body"]
    data = yaml.safe_load(yaml_path.read_text())
    tools = data["tools"]
    assert len(tools) == len(orig_tools) + 1
    assert tools[last + 1]["slug"] == "acme-canvas-mcp"
    assert tools[last]["slug"] == orig_tools[last]["slug"]
    rest = [t for t in tools if t["slug"] != "acme-canvas-mcp"]
    assert dump_yaml(rest) == dump_yaml(orig_tools)
    added = tools[last + 1]
    assert added["job"] == "connect-agents-to-design-files"
    assert added["kind"] == "mcp-server"
    assert added["mcp_server"] == "mentioned-on-page"
    assert added["repo"] == "acme/canvas-mcp"
    assert added["last_checked"] == "2026-11-10"


def test_main_idempotent_from_original_yaml(tmp_path, monkeypatch):
    code1, _, yaml_path = _run(tmp_path, monkeypatch, _body("issue_valid.md"))
    assert code1 == 0
    first = yaml_path.read_bytes()
    shutil.copy(ROOT / "data/tools.yaml", yaml_path)
    out = tmp_path / "result.json"
    monkeypatch.setenv("ISSUE_BODY", _body("issue_valid.md"))
    code2 = main(
        [
            "--root",
            str(tmp_path),
            "--issue",
            "7",
            "--out",
            str(out),
            "--no-network",
            "--today",
            "2026-11-10",
        ]
    )
    assert code2 == 0
    assert yaml_path.read_bytes() == first


def test_main_duplicate_on_already_updated_yaml(tmp_path, monkeypatch):
    code1, _, yaml_path = _run(tmp_path, monkeypatch, _body("issue_valid.md"))
    assert code1 == 0
    before = yaml_path.read_bytes()
    out = tmp_path / "result2.json"
    monkeypatch.setenv("ISSUE_BODY", _body("issue_valid.md"))
    code2 = main(
        [
            "--root",
            str(tmp_path),
            "--issue",
            "7",
            "--out",
            str(out),
            "--no-network",
            "--today",
            "2026-11-10",
        ]
    )
    assert code2 == 0
    result = json.loads(out.read_text())
    assert result["status"] == "duplicate"
    assert result["duplicate_of"]["reason"] == "same URL"
    assert yaml_path.read_bytes() == before


def test_main_existing_branch_reuse(tmp_path, monkeypatch):
    _, result, _ = _run(
        tmp_path,
        monkeypatch,
        _body("issue_valid.md"),
        env={"EXISTING_BRANCH": "add-tool/7-old-slug"},
    )
    assert result["status"] == "ok"
    assert result["branch"] == "add-tool/7-old-slug"


def test_main_existing_branch_ignored_when_pattern_mismatches(tmp_path, monkeypatch):
    _, result, _ = _run(
        tmp_path,
        monkeypatch,
        _body("issue_valid.md"),
        env={"EXISTING_BRANCH": "main"},
    )
    assert result["branch"] == "add-tool/7-acme-canvas-mcp"


def test_main_duplicate_url_leaves_yaml_and_comments(tmp_path, monkeypatch):
    before = (ROOT / "data/tools.yaml").read_bytes()
    code, result, yaml_path = _run(tmp_path, monkeypatch, _body("issue_dup_url.md"))
    assert code == 0
    assert result["status"] == "duplicate"
    assert result["duplicate_of"]["slug"] == "penpot"
    assert result["duplicate_of"]["reason"] == "same URL"
    assert result["comment"].startswith("<!-- add-tool-bot -->")
    assert "Penpot" in result["comment"]
    assert "not-duplicate" in result["comment"]
    assert yaml_path.read_bytes() == before


def test_main_duplicate_name(tmp_path, monkeypatch):
    _, result, yaml_path = _run(tmp_path, monkeypatch, _body("issue_dup_name.md"))
    assert result["status"] == "duplicate"
    assert result["duplicate_of"]["reason"] == "same name"
    assert result["comment"].startswith("<!-- add-tool-bot -->")
    assert yaml_path.read_bytes() == (ROOT / "data/tools.yaml").read_bytes()


def test_main_duplicate_domain(tmp_path, monkeypatch):
    _, result, yaml_path = _run(tmp_path, monkeypatch, _body("issue_dup_domain.md"))
    assert result["status"] == "duplicate"
    assert result["duplicate_of"]["reason"] == "same site (v0.app)"
    assert "not-duplicate" in result["comment"]
    assert yaml_path.read_bytes() == (ROOT / "data/tools.yaml").read_bytes()


def test_main_invalid_leaves_yaml_and_comments(tmp_path, monkeypatch):
    before = (ROOT / "data/tools.yaml").read_bytes()
    code, result, yaml_path = _run(tmp_path, monkeypatch, _body("issue_invalid.md"))
    assert code == 0
    assert result["status"] == "invalid"
    assert result["errors"]
    assert result["comment"].startswith("<!-- add-tool-bot -->")
    assert "Edit the issue" in result["comment"]
    assert yaml_path.read_bytes() == before


def test_main_crlf_ok(tmp_path, monkeypatch):
    orig = yaml.safe_load((ROOT / "data/tools.yaml").read_text())["tools"]
    last = max(i for i, t in enumerate(orig) if t["job"] == "generate-ui")
    code, result, yaml_path = _run(tmp_path, monkeypatch, (FIXTURES / "issue_crlf.md").read_text(), issue=8)
    assert code == 0
    assert result["status"] == "ok"
    assert result["branch"] == "add-tool/8-bolt-canvas"
    tools = yaml.safe_load(yaml_path.read_text())["tools"]
    assert tools[last + 1]["slug"] == "bolt-canvas"
    assert tools[last + 1]["licence_class"] == "proprietary"
    assert tools[last + 1]["mcp_server"] == "no-evidence"
    rest = [t for t in tools if t["slug"] != "bolt-canvas"]
    assert dump_yaml(rest) == dump_yaml(orig)


def test_dump_yaml_round_trip_matches_repo_file():
    raw = (ROOT / "data/tools.yaml").read_text()
    assert dump_yaml(yaml.safe_load(raw)) == raw


import scripts.add_tool as add_tool  # noqa: E402
REPO = ROOT


def _valid_form():
    return add_tool.parse_issue_form((FIXTURES / "issue_valid.md").read_text())


@pytest.mark.parametrize("field,value", [
    ("name", "$(touch /tmp/pwned)"),
    ("licence", "MIT `$(id)`"),
    ("description", "Hi <script>alert(1)</script>"),
    ("affiliation", "maybe"),
    ("mcp", "definitely"),
])
def test_validate_form_rejects_hostile_or_unknown_values(field, value):
    form = _valid_form()
    form[field] = value
    assert add_tool.validate_form(form)


def test_main_output_passes_build_and_validate(tmp_path, monkeypatch):
    """The yaml the bot writes must pass the repo's own validate.py and build.py."""
    import shutil, subprocess
    for rel in ("scripts", "data"):
        shutil.copytree(REPO / rel, tmp_path / rel, ignore=shutil.ignore_patterns("__pycache__"))
    monkeypatch.setenv("ISSUE_BODY", (FIXTURES / "issue_valid.md").read_text())
    monkeypatch.delenv("EXISTING_BRANCH", raising=False)
    out = tmp_path / "result.json"
    assert add_tool.main(["--root", str(tmp_path), "--issue", "7", "--out", str(out), "--no-network", "--today", "2026-11-10"]) == 0
    for script in ("validate.py", "build.py"):
        r = subprocess.run([sys.executable, str(tmp_path / "scripts" / script)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
    assert "Acme Canvas MCP" in (tmp_path / "README.md").read_text()


def test_issue_form_matches_parser():
    """The issue form must parse as YAML and use the labels and options the bot expects."""
    form = yaml.safe_load((REPO / ".github/ISSUE_TEMPLATE/add-tool.yml").read_text())
    expected = {"job": add_tool.JOBS, "kind": add_tool.KINDS, "runs": add_tool.RUNS,
                "price": add_tool.PRICE_MODELS, "affiliation": add_tool.AFFILIATIONS, "mcp": add_tool.MCP_ANSWERS}
    fields = [b for b in form["body"] if b["type"] != "markdown"]
    assert {add_tool._LABELS[b["attributes"]["label"]] for b in fields} == set(add_tool._LABELS.values())
    for b in fields:
        if b["id"] in expected:
            assert [str(o) for o in b["attributes"]["options"]] == expected[b["id"]]
    checks = next(b for b in fields if b["id"] == "checks")["attributes"]["options"]
    assert checks[0]["label"].startswith(add_tool._CHECK_PREFIX)
