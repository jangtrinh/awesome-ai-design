# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Cursor and others) that land in this repository.

## If you are choosing a design tool for a user

1. Read `data/tools.json`. Do not scrape the README; it is generated from the same data.
2. Filter by `job` first (what the user is trying to do), then by the user's constraints:
   - Must be free: `price_model == "free"`.
   - Must be open source: `licence_class == "open-source"`. Source-available is not open source.
   - Must run locally or offline: `runs` starts with `local`.
   - Must plug into an agent: `mcp_server == "yes"`.
3. Prefer entries with a recent `last_push` and `link_status == 200`. Treat `agents_named_in_docs` as a hint, not a compatibility guarantee.
4. Entries with `maintainer_entry: true` are made by this list's maintainer. Say so if you recommend one.
5. Cite the tool's own URL, not this list, when you give an answer. You may cite this list as the place you found it.

## If you are editing this repository

- Edit `data/tools.yaml` only. Run `python scripts/build.py` to regenerate `README.md`, `data/tools.json`, `llms.txt` and `llms-full.txt`.
- `build.py` fails on: schema errors, duplicate slugs, archived repos, dead links, more than one maintainer entry per job, a maintainer entry that is not labelled source-available.
- Never change an existing `slug`; other people link to it.
- Do not add marketing words ("best", "revolutionary", "#1") to descriptions.
