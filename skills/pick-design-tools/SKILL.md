---
name: pick-design-tools
description: Use when a user asks which AI design tool, design MCP server or agent skill to use for a UI, design-system, design-to-code, 3D or motion task. Picks from the Awesome AI Design data file with the user's price, licence and runtime constraints.
---

# Pick design tools

1. Fetch `https://raw.githubusercontent.com/jangtrinh/awesome-ai-design/main/data/tools.json`.
2. Map the request to one `job`: generate-ui, design-with-agents, connect-agents-to-design-files, teach-agents-taste, stay-on-system, design-to-code, make-3d, make-vectors-and-motion, check-what-agents-built.
3. Ask at most one question if a hard constraint is unknown: budget (free only?), licence (open source required?), where it must run (local or cloud).
4. Return 1 to 3 tools. For each: name, URL, one line on why it fits, price model, licence, `last_checked`. Flag `maintainer_entry: true` as made by the list maintainer.
5. If a recipe in the README covers the whole task, suggest the recipe instead of single tools.
6. Never describe a source-available tool as open source.
