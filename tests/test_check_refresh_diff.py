import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_refresh_diff import (  # noqa: E402
    ALLOWED_PATHS,
    check_refresh_diff,
    compare_paths,
    compare_yaml,
    main,
    star_jump_error,
)


def entry(slug: str, **overrides) -> dict:
    tool = {
        "slug": slug,
        "name": slug,
        "url": f"https://example.com/{slug}",
        "job": "generate-ui",
        "kind": "app",
        "licence": "MIT",
        "description": "A design tool",
        "repo": f"acme/{slug}",
        "stars": 100,
        "last_push": "2026-11-01",
        "archived": False,
        "link_status": 200,
        "last_checked": "2026-11-10",
    }
    tool.update(overrides)
    return tool


def document(*tools, **top) -> dict:
    data = {"schema_version": 1, "generated_from": "test", "tools": list(tools)}
    data.update(top)
    return data


def tweaked(data: dict, slug: str, **fields) -> dict:
    clone = yaml.safe_load(yaml.safe_dump(data))
    for tool in clone["tools"]:
        if tool["slug"] == slug:
            tool.update(fields)
            return clone
    raise KeyError(slug)


BASE = document(entry("alpha"), entry("beta", stars=200), entry("gamma", stars=None))


def test_stars_only_passes():
    head = tweaked(BASE, "alpha", stars=110, last_push="2026-11-08", last_checked="2026-11-11")
    assert compare_yaml(BASE, head) == []


def test_each_allowed_field_alone_passes():
    assert compare_yaml(BASE, tweaked(BASE, "alpha", stars=120)) == []
    assert compare_yaml(BASE, tweaked(BASE, "alpha", last_push="2026-11-09")) == []
    assert compare_yaml(BASE, tweaked(BASE, "alpha", last_checked="2026-11-12")) == []


def test_identical_documents_pass():
    assert compare_yaml(BASE, yaml.safe_load(yaml.safe_dump(BASE))) == []


def test_stars_from_none_within_cap_passes():
    assert compare_yaml(BASE, tweaked(BASE, "gamma", stars=40)) == []


def test_star_jump_boundaries():
    assert star_jump_error("alpha", 100, 150) is None  # exactly 50%
    assert star_jump_error("alpha", 10000, 15000) is None  # exactly 5,000
    assert "over 50%" in star_jump_error("alpha", 100, 151)
    assert "over 5,000" in star_jump_error("alpha", 20000, 25001)
    assert star_jump_error("alpha", None, 5000) is None
    assert "over 5,000" in star_jump_error("gamma", None, 5001)
    assert "over 50%" in star_jump_error("alpha", 100, 40)  # a drop also fails


def test_star_jump_over_fifty_percent_fails():
    errors = compare_yaml(BASE, tweaked(BASE, "alpha", stars=200))
    assert any("alpha: stars:" in e and "over 50%" in e for e in errors)


def test_star_jump_over_five_thousand_fails():
    errors = compare_yaml(BASE, tweaked(BASE, "beta", stars=5700))  # 200 -> 5700 is both, but abs trips first if > 5000
    # 5500 jump is over 5,000
    assert any("beta: stars:" in e and "over 5,000" in e for e in errors)
    # under 50% (25%) but over 5,000
    large = document(entry("penpot", stars=20000))
    errors = compare_yaml(large, tweaked(large, "penpot", stars=25001))
    assert any("over 5,000" in e for e in errors)
    assert not any("over 50%" in e for e in errors)


def test_disallowed_field_changes_fail():
    cases = {
        "link_status": 404,
        "archived": True,
        "description": "changed",
        "url": "https://example.com/other",
        "licence": "Apache-2.0",
        "name": "Alpha",
        "repo": "acme/other",
    }
    for field, value in cases.items():
        errors = compare_yaml(BASE, tweaked(BASE, "alpha", **{field: value}))
        assert errors, f"{field} should fail"
        assert any(f"alpha: {field}: changed" in e for e in errors), errors


def test_key_added_or_removed_fails():
    head = tweaked(BASE, "alpha", extra="nope")
    assert any("alpha: extra: key added" in e for e in compare_yaml(BASE, head))
    head = yaml.safe_load(yaml.safe_dump(BASE))
    del head["tools"][0]["licence"]
    assert any("alpha: licence: key removed" in e for e in compare_yaml(BASE, head))


def test_top_level_change_fails():
    head = yaml.safe_load(yaml.safe_dump(BASE))
    head["generated_from"] = "other"
    errors = compare_yaml(BASE, head)
    assert any("(document): generated_from: changed" in e for e in errors)


def test_slug_added_removed_or_moved_fails():
    added = document(entry("alpha"), entry("beta", stars=200), entry("gamma", stars=None), entry("delta"))
    removed = document(entry("alpha"), entry("beta", stars=200))
    moved = document(entry("alpha"), entry("gamma", stars=None), entry("beta", stars=200))
    assert any("delta: slug added" in e for e in compare_yaml(BASE, added))
    assert any("gamma: slug removed" in e for e in compare_yaml(BASE, removed))
    moved_errors = compare_yaml(BASE, moved)
    assert any("slug list changed" in e for e in moved_errors)
    assert any("slug moved" in e for e in moved_errors)
    # field diffs of misaligned pairs must not be reported when the list changed
    assert not any("changed" in e and ": stars:" not in e for e in moved_errors if "moved" not in e and "list" not in e)


def test_allowed_paths_pass_and_unexpected_paths_fail():
    assert compare_paths(sorted(ALLOWED_PATHS)) == []
    assert compare_paths(["data/tools.yaml", "README.md"]) == []
    errors = compare_paths(["data/tools.yaml", "CHANGELOG.md", "scripts/build.py"])
    assert errors == [
        "(files): unexpected path CHANGELOG.md",
        "(files): unexpected path scripts/build.py",
    ]


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Jang Trinh")
    _git(repo, "config", "user.email", "6948894+jangtrinh@users.noreply.github.com")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "data").mkdir()
    (repo / "data" / "tools.yaml").write_text(yaml.safe_dump(BASE, sort_keys=False))
    (repo / "README.md").write_text("list\n")
    (repo / "data" / "tools.json").write_text("{}\n")
    (repo / "llms.txt").write_text("llms\n")
    (repo / "llms-full.txt").write_text("llms-full\n")
    (repo / "CHANGELOG.md").write_text("changelog\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "base")
    _git(repo, "branch", "-M", "main")
    return repo


def _commit_head(repo: Path, message: str = "refresh") -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


def test_cli_stars_only_with_generated_files_passes(tmp_path):
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "weekly-refresh")
    head = tweaked(BASE, "alpha", stars=110, last_checked="2026-11-11")
    (repo / "data" / "tools.yaml").write_text(yaml.safe_dump(head, sort_keys=False))
    (repo / "README.md").write_text("list with 110 stars\n")
    (repo / "data" / "tools.json").write_text('{"stars": 110}\n')
    (repo / "llms.txt").write_text("llms 110\n")
    (repo / "llms-full.txt").write_text("llms-full 110\n")
    _commit_head(repo)
    assert check_refresh_diff(str(repo), "main", "weekly-refresh") == []
    assert main(["--repo", str(repo), "--base", "main", "--head", "weekly-refresh"]) == 0


def test_cli_rejects_disallowed_field(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "weekly-refresh")
    (repo / "data" / "tools.yaml").write_text(
        yaml.safe_dump(tweaked(BASE, "alpha", link_status=500), sort_keys=False)
    )
    _commit_head(repo)
    errors = check_refresh_diff(str(repo), "main", "weekly-refresh")
    assert any("alpha: link_status: changed" in e for e in errors)
    assert main(["--repo", str(repo), "--base", "main", "--head", "weekly-refresh"]) == 1
    out = capsys.readouterr().out
    assert "alpha: link_status: changed" in out


def test_cli_rejects_unexpected_file(tmp_path, capsys):
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "weekly-refresh")
    (repo / "data" / "tools.yaml").write_text(
        yaml.safe_dump(tweaked(BASE, "alpha", stars=110), sort_keys=False)
    )
    (repo / "CHANGELOG.md").write_text("also edited\n")
    _commit_head(repo)
    errors = check_refresh_diff(str(repo), "main", "weekly-refresh")
    assert any("unexpected path CHANGELOG.md" in e for e in errors)
    assert main(["--repo", str(repo), "--base", "main", "--head", "weekly-refresh"]) == 1
    assert "CHANGELOG.md" in capsys.readouterr().out


def test_cli_rejects_invalid_head_yaml(tmp_path):
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "weekly-refresh")
    (repo / "data" / "tools.yaml").write_text(": this is not valid: [")
    _commit_head(repo)
    errors = check_refresh_diff(str(repo), "main", "weekly-refresh")
    assert any("does not parse" in e for e in errors)


def test_weekly_workflow_is_gated_and_not_triggered_by_pull_requests():
    text = (ROOT / ".github/workflows/check.yml").read_text()
    # Trigger block must stay schedule / workflow_dispatch only.
    start = text.index("\non:")
    end = text.index("\njobs:")
    triggers = text[start:end]
    assert "pull_request" not in triggers
    assert "AUTO_MERGE_STARS_REFRESH" in text
    assert "check_refresh_diff.py" in text
    assert "--squash --auto" in text
    assert "actions: write" in text
