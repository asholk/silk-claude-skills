---
name: obsidian-style
description: Obsidian style for text and UI — before starting work, opens the official style guide https://obsidian.md/ru/help/style-guide and applies its rules. Use always when Obsidian is mentioned or when developing, improving or reviewing an Obsidian plugin or theme (manifest.json, main.js, Plugin, Setting, Modal, Notice, .obsidian/plugins), and when writing READMEs, settings, commands, notices and documentation for them.
---

# Obsidian Style

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

## 1. Load the style guide

Before writing UI text, settings, commands, notices, a README or documentation:

1. Open `https://obsidian.md/ru/help/style-guide` via `WebFetch` (if the tool is deferred, load it first via `ToolSearch` `select:WebFetch`). Prompt: "List all the rules in full, with examples".
2. For plugin code, also load `https://docs.obsidian.md/Plugins/Releasing/Plugin+guidelines` — UI text and API rules for plugins.
3. If the page is unavailable, use the short digest in `reference.md` next to this file and tell the user so in one line.

Load it once per conversation; reload only if a lot of time has passed or the user asks.

## 2. Apply when creating

- **Plugin UI text** (`setName`, `setDesc`, `Notice`, commands, buttons, modals) — sentence case, imperative mood for actions, terms from the style guide («заметка», «папка», «сочетание клавиш», «выбрать»).
- **Settings** — section headings without the word «настройки», no top-level heading with the plugin name (a Plugin guidelines rule).
- **Commands** — no plugin name in the command name (Obsidian adds it itself), no default hotkeys.
- **README and documentation** — sentence case in headings, buttons in **bold**, navigation paths with →, key combinations like `Ctrl+Z` without spaces, callouts and `description` up to 150 characters per the guide's rules.
- **Icons** — Lucide (`setIcon(el, "lucide-name")` / the name without the prefix in the API).

Text language — whichever the user writes in or the plugin is already written in; apply the guide's rules to it.

## 3. Check

Before finishing, go through the strings you created and fix deviations from the guide. Don't list the applied rules separately in your reply — only if the user asks or if you had to deviate from the guide (then in one line: what and why).
