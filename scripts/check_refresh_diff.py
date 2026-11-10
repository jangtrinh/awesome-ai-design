"""Check that a weekly-refresh branch only updates stars, last_push and last_checked.

Loads data/tools.yaml from two git refs (the pull request base and head). Exits 0
only if every other field and the file list are unchanged, slugs stay in the
same order, and no star count moved by more than 50% or 5,000. Prints each
failing slug and field, then exits 1 on any failure.

A link_status, archived, description, url, licence or any other unexpected
change is left for a person to review.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

import yaml

ALLOWED_PATHS = frozenset(
    {
        "data/tools.yaml",
        "README.md",
        "data/tools.json",
        "llms.txt",
        "llms-full.txt",
    }
)
ALLOWED_FIELDS = frozenset({"stars", "last_push", "last_checked"})
STAR_JUMP_RATIO = 0.5
STAR_JUMP_ABS = 5000
TOOLS_PATH = "data/tools.yaml"


def _run_git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", repo, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def diff_paths(repo: str, base: str, head: str) -> tuple[list[str], str | None]:
    proc = _run_git(repo, "diff", "--name-only", "--no-renames", base, head)
    if proc.returncode != 0:
        return [], (proc.stderr or proc.stdout).strip() or "git diff failed"
    paths = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return paths, None


def show_file(repo: str, ref: str, path: str) -> tuple[str | None, str | None]:
    proc = _run_git(repo, "show", f"{ref}:{path}")
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout).strip() or f"git show {ref}:{path} failed"
    return proc.stdout, None


def _preview(value, limit: int = 80) -> str:
    text = repr(value)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def _star_number(value):
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def star_jump_error(slug: str, old, new) -> str | None:
    if old == new:
        return None
    old_n, new_n = _star_number(old), _star_number(new)
    if old_n is None or new_n is None:
        return f"{slug}: stars: type changed ({_preview(old)} -> {_preview(new)})"
    delta = abs(new_n - old_n)
    if delta > STAR_JUMP_ABS:
        return f"{slug}: stars: {old} -> {new} (moved by {delta}, over 5,000)"
    if isinstance(old, (int, float)) and not isinstance(old, bool) and old != 0:
        if delta / abs(old) > STAR_JUMP_RATIO:
            pct = 100.0 * delta / abs(old)
            return f"{slug}: stars: {old} -> {new} (moved by {pct:.1f}%, over 50%)"
    return None


def slug_list_errors(base_tools: list, head_tools: list) -> list[str]:
    def slugs(tools: list) -> list:
        return [t.get("slug") if isinstance(t, dict) else None for t in tools]

    base_slugs, head_slugs = slugs(base_tools), slugs(head_tools)
    if base_slugs == head_slugs:
        return []

    errors = ["(document): tools: slug list changed (added, removed or moved)"]
    base_set, head_set = set(base_slugs), set(head_slugs)
    for slug in base_slugs:
        if slug in base_set - head_set:
            errors.append(f"{slug}: slug removed")
    for slug in head_slugs:
        if slug in head_set - base_set:
            errors.append(f"{slug}: slug added")
    if base_set == head_set:
        for index, (old, new) in enumerate(zip(base_slugs, head_slugs)):
            if old != new:
                errors.append(f"tools[{index}]: slug moved (expected {old}, found {new})")
    return errors


def compare_entries(base: dict, head: dict, slug: str) -> list[str]:
    errors = []
    base_keys, head_keys = set(base), set(head)
    for key in sorted(head_keys - base_keys):
        errors.append(f"{slug}: {key}: key added")
    for key in sorted(base_keys - head_keys):
        errors.append(f"{slug}: {key}: key removed")
    for key in sorted(base_keys & head_keys):
        if key in ALLOWED_FIELDS:
            if key == "stars":
                jump = star_jump_error(slug, base[key], head[key])
                if jump:
                    errors.append(jump)
            continue
        if base[key] != head[key]:
            errors.append(
                f"{slug}: {key}: changed ({_preview(base[key])} -> {_preview(head[key])})"
            )
    return errors


def compare_yaml(base_data, head_data) -> list[str]:
    errors = []
    if not isinstance(base_data, dict) or not isinstance(head_data, dict):
        return ["(document): tools.yaml must be a mapping with a tools list"]
    if not isinstance(base_data.get("tools"), list) or not isinstance(head_data.get("tools"), list):
        return ["(document): tools.yaml must be a mapping with a tools list"]

    base_keys, head_keys = set(base_data), set(head_data)
    for key in sorted(head_keys - base_keys):
        errors.append(f"(document): {key}: key added")
    for key in sorted(base_keys - head_keys):
        errors.append(f"(document): {key}: key removed")
    for key in sorted(base_keys & head_keys):
        if key == "tools":
            continue
        if base_data[key] != head_data[key]:
            errors.append(
                f"(document): {key}: changed ({_preview(base_data[key])} -> {_preview(head_data[key])})"
            )

    slug_errors = slug_list_errors(base_data["tools"], head_data["tools"])
    errors.extend(slug_errors)
    if slug_errors:
        return errors

    for index, (base_entry, head_entry) in enumerate(
        zip(base_data["tools"], head_data["tools"])
    ):
        if not isinstance(base_entry, dict) or not isinstance(head_entry, dict):
            errors.append(f"tools[{index}]: entry must be a mapping")
            continue
        slug = base_entry.get("slug") or f"tools[{index}]"
        errors.extend(compare_entries(base_entry, head_entry, slug))
    return errors


def compare_paths(paths: list[str]) -> list[str]:
    unexpected = sorted(set(paths) - ALLOWED_PATHS)
    return [f"(files): unexpected path {path}" for path in unexpected]


def check_refresh_diff(repo: str, base: str, head: str) -> list[str]:
    errors: list[str] = []
    paths, diff_err = diff_paths(repo, base, head)
    if diff_err:
        return [f"(git): {diff_err}"]
    errors.extend(compare_paths(paths))

    base_text, base_err = show_file(repo, base, TOOLS_PATH)
    head_text, head_err = show_file(repo, head, TOOLS_PATH)
    if base_err:
        errors.append(f"(git): base {TOOLS_PATH}: {base_err}")
    if head_err:
        errors.append(f"(git): head {TOOLS_PATH}: {head_err}")
    if base_err or head_err:
        return errors

    try:
        base_data = yaml.safe_load(base_text)
    except yaml.YAMLError as exc:
        return errors + [f"(document): base {TOOLS_PATH} does not parse: {exc}"]
    try:
        head_data = yaml.safe_load(head_text)
    except yaml.YAMLError as exc:
        return errors + [f"(document): head {TOOLS_PATH} does not parse: {exc}"]
    errors.extend(compare_yaml(base_data, head_data))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Git ref for the pull request base (e.g. origin/main)")
    parser.add_argument("--head", required=True, help="Git ref for the pull request head (e.g. weekly-refresh)")
    parser.add_argument("--repo", default=".", help="Path to the git repository (default: current directory)")
    args = parser.parse_args(argv)

    errors = check_refresh_diff(args.repo, args.base, args.head)
    if errors:
        for line in errors:
            print(line)
        print(f"\n{len(errors)} problem(s). Leave the pull request for review.")
        return 1
    print("ok: refresh only changes stars, last_push and last_checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
