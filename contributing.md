# Contribution Guidelines

This list stays useful only if every entry earns its place.

## Add a tool

1. Open an issue with the **Add a tool** form. A bot checks the form, looks for duplicates (same URL, same name, or same site) and opens a draft pull request that closes your issue. If it finds a problem it labels the issue and leaves one comment; edit the issue to fix it and the bot runs again. A maintainer reviews the draft, marks it ready for review (which starts CI) and merges it. Or:
2. Edit `data/tools.yaml`, add one entry at the end of its `job`, run `python scripts/build.py`, and open a pull request titled `Add Name`. CI fails if the generated files do not match `data/tools.yaml`.

Do not edit `README.md`, `data/tools.json` or the `llms*.txt` files by hand. They are generated.

## What gets in

1. **It helps AI do real design work.** Interface, visual, 3D, motion or UX work where a model or agent does the work, not a tool that only adds an AI label.
2. **It works today.** Link returns 200, the repo is not archived, there is a commit or release in the last 6 months.
3. **It has docs** that explain how to install or use it.
4. **Price and licence are clear.** Use the `price_model` and `licence_class` values in the schema. Source-available is never called open source.
5. **It is not a duplicate.** If it overlaps an entry, say in the PR what it does better.

## What stays out

- Generic image or video generators whose output is not an editable design asset.
- Prompt packs, GPTs, wallpapers, and galleries of generated images.
- Research papers (see the related lists).
- Single brand DESIGN.md files (see the DESIGN.md list).
- Affiliate, referral or tracking links, and descriptions written as ads.

## Disclose

Say in the PR if you made, work on or are paid by the project. Disclosed entries are welcome and judged by the same rules. The maintainer's own tools follow the same rules, are capped at one per section, and never appear in Start here.

## Upkeep

`scripts/check_links.py` runs every week. An entry that fails two checks in a row, gets archived, or has no commit for 6 months is removed, with a line in `CHANGELOG.md`.
