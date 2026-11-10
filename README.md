# Awesome AI Design [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> Tools, MCP servers and agent skills that let AI take part in interface, 3D and motion design.

57 entries, organised by the job you are doing. Each entry carries its price model, licence, where it runs, whether it is an MCP server, and the date its link was last checked. The same data is in [`data/tools.json`](data/tools.json) for scripts and agents, with a summary in [`llms.txt`](llms.txt).

## Contents

- [Start here](#start-here)
- [Generate UI from a prompt](#generate-ui-from-a-prompt)
- [Design with an agent on the canvas](#design-with-an-agent-on-the-canvas)
- [Connect agents to design files](#connect-agents-to-design-files)
- [Teach agents taste](#teach-agents-taste)
- [Keep output on your design system](#keep-output-on-your-design-system)
- [Turn designs into code](#turn-designs-into-code)
- [Make 3D with agents](#make-3d-with-agents)
- [Make vectors and motion](#make-vectors-and-motion)
- [Check what agents built](#check-what-agents-built)
- [Compare: agent access to design files](#compare-agent-access-to-design-files)
- [Stack recipes](#stack-recipes)
- [Related lists](#related-lists)

## Start here

Three picks per reader, all listed below. Maintainer-made tools are never in this section.

| Reader                                        | Start with                                                        |
| --------------------------------------------- | ----------------------------------------------------------------- |
| Product designer trying AI agents             | Google Stitch, Penpot MCP server, UI UX Pro Max                   |
| Design engineer wiring agents to design files | Figma MCP server (official), shadcn/ui MCP server, Playwright MCP |
| Indie maker working in 3D or motion           | MCP for Blender, TRELLIS.2, Remotion Agent Skills                 |

Tags read `price · licence · where it runs · MCP · stars · last checked`.

## Generate UI from a prompt

Prompt, sketch or screenshot in; screens, prototypes or running apps out.

- [v0](https://v0.app) - Vercel's chat-to-app builder that generates React, Tailwind and shadcn/ui interfaces. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Google Stitch](https://stitch.withgoogle.com) - Google Labs experiment that turns prompts or sketches into UI designs and front-end code. `Price unverified · proprietary · cloud · checked 2026-11-10`.
- [Uizard](https://uizard.io) - Generates multi-screen app and web mockups from text, screenshots or hand-drawn sketches. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Magic Patterns](https://www.magicpatterns.com) - Prompt-to-prototype tool that can build on your own design system components. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [UX Pilot](https://uxpilot.ai) - Generates wireframes and hi-fi screens and exports them to design files and code. `Price unverified · proprietary · cloud · checked 2026-11-10`.
- [Relume](https://www.relume.io) - Generates sitemaps and wireframes for marketing sites, then exports to Webflow or design files. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Subframe](https://www.subframe.com) - Visual editor with AI generation that outputs React and Tailwind code. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Bolt.new](https://bolt.new) - StackBlitz's in-browser AI app builder that generates, runs and deploys full-stack web apps from a prompt. `Freemium · proprietary · cloud · checked 2026-11-10`.

## Design with an agent on the canvas

Design editors where a person and an agent work on the same file.

- [DESIGN:OS Studio](https://github.com/jangtrinh/design-os-studio) - GPU-accelerated desktop interface design tool built in Rust, with a built-in MCP server so coding agents can read and edit the canvas. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · MCP · 87 stars · checked 2026-11-10`.
- [Penpot](https://github.com/penpot/penpot) - Open-source design and prototyping platform that also ships an official MCP server. `Free · open source (MPL-2.0) · cloud or self-hosted · 62.2k stars · checked 2026-11-10`.
- [Onlook](https://github.com/onlook-dev/onlook) - Visual editor for React and Tailwind apps where you design in the browser and an AI agent writes the code. `Free · open source (Apache-2.0) · cloud or local · 27.2k stars · checked 2026-11-10`.
- [Framer](https://www.framer.com) - Website builder with AI page generation, AI translation and on-canvas AI tools. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Wonder](https://wonder.design) - Desktop and browser canvas where you and Claude Code or Codex design on your live app, then apply the changes back to the code. `Freemium · proprietary · local or browser · checked 2026-11-10`.
- [Dessn](https://www.dessn.ai) - Design canvas that runs your production app from its codebase, so you and coding agents can prototype, audit design drift and ship changes over MCP. `Freemium · proprietary · cloud · MCP · checked 2026-11-10`.

## Connect agents to design files

MCP servers and bridges that let Claude Code, Codex, Cursor and other agents read and write design files.

- [Figma MCP server (official)](https://github.com/figma/mcp-server-guide) - Figma's official MCP server guide: gives coding agents design context, variables and code connect data. `Freemium · proprietary · remote or desktop · MCP · 2.2k stars · checked 2026-11-10`.
- [Framelink MCP for Figma](https://github.com/GLips/Figma-Context-MCP) - Community MCP server that gives coding agents simplified layout and style data from Figma files. `Free · open source (MIT) · local · MCP · 16.2k stars · checked 2026-11-10`.
- [Cursor Talk to Figma MCP](https://github.com/grab/cursor-talk-to-figma-mcp) - Plugin plus MCP server that lets Cursor and other agents read and modify Figma designs. `Free · open source (MIT) · local · MCP · 7.1k stars · checked 2026-11-10`.
- [DESIGN:OS Bridge](https://github.com/jangtrinh/design-os-figma-plugin) - Plugin plus CLI that works with Figma: Claude Code, Codex or any shell agent can read and edit the open file over a local WebSocket, one undo step per change. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · 25 stars · checked 2026-11-10`.
- [Penpot MCP server](https://help.penpot.app/mcp/) - Official MCP server for Penpot so agents can inspect and change Penpot designs. `Free · open source (proprietary (SaaS)) · remote or local · MCP · checked 2026-11-10`.
- [Magic MCP (21st.dev)](https://github.com/21st-dev/magic-mcp) - MCP server that generates UI components from natural-language prompts inside your IDE. `Freemium · proprietary · local (API key) · MCP · 6.4k stars · checked 2026-11-10`.
- [shadcn/ui MCP server](https://ui.shadcn.com/docs/mcp) - Lets agents browse, search and install components from shadcn/ui-compatible registries. `Free · proprietary · local · MCP · checked 2026-11-10`.
- [Canva MCP server](https://www.canva.dev/docs/connect/canva-mcp-server-setup/) - Official Canva MCP server for creating and editing Canva designs from AI assistants. `Freemium · proprietary · see docs · MCP · checked 2026-11-10`.

## Teach agents taste

Skills, specs and guidelines that change what an agent designs, not only how fast.

- [Anthropic Skills (frontend-design)](https://github.com/anthropics/skills) - Official Agent Skills repo; the frontend-design skill steers agents away from generic-looking UI. `Free · licence varies · local · 191.2k stars · checked 2026-11-10`.
- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) - Agent skill with searchable styles, palettes, font pairings and UX rules for building UI. `Free · open source (MIT) · local · 147.4k stars · checked 2026-11-10`.
- [DESIGN.md](https://github.com/google-labs-code/design.md) - Format for describing a visual identity to coding agents in a single markdown file. `Free · open source (Apache-2.0) · n/a · 28.8k stars · checked 2026-11-10`.
- [Awesome DESIGN.md](https://github.com/VoltAgent/awesome-design-md) - Collection of DESIGN.md files that capture popular brand design systems for agents. `Free · open source (MIT) · n/a · 126.4k stars · checked 2026-11-10`.
- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) - Vercel's interface quality rules, packaged so agents can review UI against them. `Free · open source (MIT) · n/a · 1.1k stars · checked 2026-11-10`.
- [design:os CLI](https://github.com/jangtrinh/design-os) - Design CLI and skills for Claude Code, Codex and Antigravity: describe a UI in plain words and get web, SwiftUI or design-file output checked by deterministic taste gates. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · 37 stars · checked 2026-11-10`.
- [evondevKit](https://github.com/evondev/evondevKit) - Agent skill that walks coding agents through a brief, wireframes and a shared design system before they build UI, then measures layout issues in a real browser. `Free · open source (MIT) · local · 533 stars · checked 2026-11-10`.

## Keep output on your design system

Components, tokens and docs that keep generated UI on-brand.

- [shadcn/ui](https://github.com/shadcn-ui/ui) - Copy-in component system and registry that most AI UI generators target. `Free · open source (MIT) · local · 127.8k stars · checked 2026-11-10`.
- [Style Dictionary](https://github.com/style-dictionary/style-dictionary) - Build system that turns design tokens into platform code, a common target for agent token pipelines. `Free · open source (Apache-2.0) · local · 4.9k stars · checked 2026-11-10`.
- [Tokens Studio](https://github.com/tokens-studio/figma-plugin) - Manage design tokens in a design file and sync them with Git for code and agent use. `Freemium · open source (MIT) · in design app · 1.6k stars · checked 2026-11-10`.
- [Design Tokens Community Group format](https://github.com/design-tokens/community-group) - The W3C community group spec for interoperable design token files. `Free · proprietary · n/a · 2.2k stars · checked 2026-11-10`.
- [Storybook MCP](https://storybook.js.org/docs/ai/mcp/overview) - Exposes your Storybook components and docs to agents so generated UI reuses real components. `Free · open source (proprietary (SaaS)) · local · MCP · checked 2026-11-10`.
- [Knowns UI](https://ui.knowns.dev) - React and Tailwind component kit for AI-product interfaces, installed with the shadcn CLI. An MCP server lets coding agents search the docs. `Freemium · open source (MIT (third-party logos in the icon set are not MIT)) · local · 6 stars · checked 2026-11-10`.

## Turn designs into code

Convert a finished design into production front-end code.

- [screenshot-to-code](https://github.com/abi/screenshot-to-code) - Turns screenshots, mockups and design files into HTML, Tailwind, React or Vue code. `Free · open source (MIT) · local or hosted · 81.1k stars · checked 2026-11-10`.
- [Anima](https://www.animaapp.com) - Converts design files into React, HTML and Vue code with an AI coding layer. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Locofy](https://www.locofy.ai) - Turns designs into front-end code for React, Next.js, React Native and more. `Price unverified · proprietary · cloud · checked 2026-11-10`.
- [Builder.io Visual Copilot](https://www.builder.io/figma-to-code) - Converts design files to code in your framework and maps them to your components. `Freemium · proprietary · cloud · checked 2026-11-10`.

## Make 3D with agents

Generate, edit and check 3D assets with models and agents.

- [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) - Connects Blender to MCP clients so an agent can create, inspect and edit 3D scenes. `Free · open source (MIT) · local · MCP · 33.8k stars · checked 2026-11-10`.
- [DESIGN:OS 3D Blender](https://github.com/jangtrinh/design-os-3d-blender) - Agent operating system for Blender 5.2: bpy knowledge base, execution contract and a 3D-print production gate. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · MCP · 113 stars · checked 2026-11-10`.
- [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) - Microsoft's image-to-3D model that generates textured meshes. `Free · open source (MIT) · local (GPU) · 12.8k stars · checked 2026-11-10`.
- [Meshy](https://www.meshy.ai) - Text and image to 3D model generator with texturing and export to common formats. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Tripo](https://www.tripo3d.ai) - AI 3D model generator from text or images, with auto-rigging. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Spline](https://spline.design) - Browser 3D design tool with AI generation of 3D objects and textures. `Freemium · proprietary · cloud · checked 2026-11-10`.

## Make vectors and motion

Vector generation, vectorising and agent-driven animation.

- [Remotion](https://github.com/remotion-dev/remotion) - Make videos with React; widely used by coding agents for programmatic motion. `Free for individuals · source-available (Remotion License (read from LICENSE.md)) · local · 72.1k stars · checked 2026-11-10`.
- [Remotion Agent Skills](https://github.com/remotion-dev/skills) - Official agent skills that teach coding agents to write Remotion videos. `Free · licence unclear · local · 6.7k stars · checked 2026-11-10`.
- [DESIGN:OS SVG Animation](https://github.com/jangtrinh/design-os-svg-animation) - Deterministic vector animation and 1080p 60fps video pipeline for AI agents. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · 8 stars · checked 2026-11-10`.
- [VTracer](https://github.com/visioncortex/vtracer) - Converts raster images, including AI-generated ones, into clean SVG. `Free · open source (MIT) · local · 7.5k stars · checked 2026-11-10`.
- [Recraft](https://www.recraft.ai) - Image generator that outputs editable vector graphics, icons and brand-consistent styles. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Rive](https://rive.app) - Interactive animation editor and runtimes for state-machine driven motion. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Jitter](https://jitter.video) - Motion design tool for UI and product animations, exports to video and Lottie. `Freemium · proprietary · cloud · checked 2026-11-10`.
- [Clayzo](https://www.clayzo.com) - Animation engine for coding agents that write a typed motion document, check the frames, and export video or an interactive web or Swift player. `Free · proprietary · local · checked 2026-11-10`.

## Check what agents built

Screenshots, accessibility checks and user flows, so an agent can verify its own output.

- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - Lets agents drive a real browser to check generated UI with screenshots and accessibility snapshots. `Free · open source (Apache-2.0) · local · MCP · 39.4k stars · checked 2026-11-10`.
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) - Gives agents DevTools access for layout, performance and visual debugging of what they built. `Free · open source (Apache-2.0) · local · MCP · 55.0k stars · checked 2026-11-10`.
- [axe-core](https://github.com/dequelabs/axe-core) - Accessibility testing engine that agents can run against generated UI. `Free · open source (MPL-2.0) · local · 7.8k stars · checked 2026-11-10`.
- [DESIGN:OS code2flow](https://github.com/jangtrinh/design-os-code2flow) - Turns a Next.js codebase into a user-flow canvas with real screenshots per screen and code-evidenced transitions, 100% local. Disclosure: made by the maintainer of this list. `FREE · source-available (PolyForm Shield) · local · 9 stars · checked 2026-11-10`.

## Compare: agent access to design files

| Tool                        | Type           | Runs              | Price    | Licence                                              |
| --------------------------- | -------------- | ----------------- | -------- | ---------------------------------------------------- |
| Figma MCP server (official) | mcp-server     | remote or desktop | Freemium | proprietary service (guide repo has no licence file) |
| Framelink MCP for Figma     | mcp-server     | local             | Free     | MIT                                                  |
| Cursor Talk to Figma MCP    | mcp-server     | local             | Free     | MIT                                                  |
| DESIGN:OS Bridge            | plugin-and-cli | local             | FREE     | source-available (PolyForm Shield)                   |
| Penpot MCP server           | mcp-server     | remote or local   | Free     | proprietary (SaaS)                                   |
| Magic MCP (21st.dev)        | mcp-server     | local (API key)   | Freemium | ISC                                                  |
| shadcn/ui MCP server        | mcp-server     | local             | Free     | proprietary (SaaS)                                   |
| Canva MCP server            | mcp-server     | see docs          | Freemium | proprietary (SaaS)                                   |

## Stack recipes

Each recipe only uses tools listed above. Steps are a starting point, not a benchmark.

### Prompt to an on-brand React screen, checked by the agent

| Step | Tool                 | What it does here                                            |
| ---- | -------------------- | ------------------------------------------------------------ |
| 1    | DESIGN.md            | Describe the brand in one file the agent reads first.        |
| 2    | UI UX Pro Max        | Give the agent style, palette and UX rules.                  |
| 3    | shadcn/ui MCP server | Let it install real components instead of inventing them.    |
| 4    | Playwright MCP       | Have it screenshot the result and compare against the brief. |
| 5    | axe-core             | Run accessibility checks before you review.                  |

### Design file to production code that reuses your components

| Step | Tool                        | What it does here                                          |
| ---- | --------------------------- | ---------------------------------------------------------- |
| 1    | Figma MCP server (official) | Give the agent the frame, variables and Code Connect data. |
| 2    | Storybook MCP               | Point it at your existing components and docs.             |
| 3    | Chrome DevTools MCP         | Let it debug layout against the running app.               |

### Agent-built 3D asset or printable part

| Step | Tool            | What it does here                                               |
| ---- | --------------- | --------------------------------------------------------------- |
| 1    | TRELLIS.2       | Start from a reference image when you have one.                 |
| 2    | MCP for Blender | Let the agent refine the mesh, materials and render in Blender. |

### Vector illustration to a rendered motion clip

| Step | Tool                  | What it does here                                                   |
| ---- | --------------------- | ------------------------------------------------------------------- |
| 1    | Recraft               | Generate an editable vector illustration.                           |
| 2    | VTracer               | Or vectorise a raster image you already have.                       |
| 3    | Remotion Agent Skills | Teach the agent Remotion, then have it animate and render the clip. |

## Related lists

- [AI Tools for UI](https://github.com/maxbogo/awesome-ai-tools-for-ui#readme) - Skills, apps and MCP servers for building UI with AI.
- [AI Design Workflows](https://github.com/humbleteam/awesome-ai-design-workflows#readme) - Standards and patterns for product teams using AI.
- [Generative UI](https://github.com/narrowin/awesome-generative-ui#readme) - Interfaces that a model renders at runtime.
- [Motion Design Agent Skills](https://github.com/frankxai/awesome-motion-design-agent-skills#readme) - Agent skills for web animation and video.
- [Blender](https://github.com/agmmnn/awesome-blender#readme) - Add-ons, tools and resources for the open-source 3D suite.
- [MCP Servers](https://github.com/punkpeye/awesome-mcp-servers#readme) - Model Context Protocol servers of every kind.
- [DESIGN.md](https://github.com/VoltAgent/awesome-design-md#readme) - Brand design systems written for agents.

## Footnotes

Read the [contribution guidelines](contributing.md) before adding a tool; edit `data/tools.yaml`, not this file. Entries marked "Disclosure: made by the maintainer of this list" meet the same criteria as every other entry, there is at most one per section, and they never appear in Start here. Links are checked every week by `scripts/check_links.py`.

