---
name: fru-fru
description: Fru-fru — "frustration" of a topic, i.e. an exhaustive brainstorm without code changes. First two independent analysts (a Claude subagent and Codex) search in parallel for material in sources of different types — from scientific papers and conference talks to engineering blogs, forums and popular magazines — then propose as many options as possible (20–40, from conservative to radical). The coordinator verifies the options against the code, merges them and outputs a concise table with idea quality and code impact, plus a sources table. Use when the user writes «фру-фру …», «фрустрация …», calls /fru-fru, or asks for the maximum number of options or ideas, a brainstorm or мозговой штурм on a topic with source research.
argument-hint: <topic for exhaustive enumeration of options>
---

# Fru-fru

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

User request: **$ARGUMENTS**

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it isn't installed, the models are given below.

"Frustration" here is an exhaustive-enumeration mode: collect as many options on the topic as possible, drawing on a wide range of sources, and rate each by quality and by code impact.

You are the coordinator. Two independent analysts — a Claude subagent and Codex — search for sources and come up with options. You set their task, verify their options and combine everything into two tables: options and sources.

**Change nothing**: don't edit or create project files, don't commit, don't run state-changing commands (package installs, migrations, formatters that write). Only reading, searching (in code and on the web), running non-writing checks and writing temporary files to the scratchpad are allowed. Pass the same restriction to both analysts.

## 1. Topic and brief

1. From the request, determine the topic and scope: which part of the code or product, which aspect (mechanics, UX, performance, graphics, architecture, reliability, new capabilities…). If the request is empty or general, take the project or area discussed most recently in the conversation and formulate the topic yourself. Don't ask clarifying questions — state the topic in one line at the start of your answer.
2. Orient yourself briefly (Glob/Grep, 2–5 calls), only to give the analysts an entry point: root, key folders or files, platform and version, constraints. Don't do deep analysis — that's the analysts' job.
3. Write a **brief** — a shared text for both analysts (only the source matrix differs, see step 2):
   - topic and scope, project root, entry points;
   - context from the conversation that isn't in the code (user goals, already rejected ideas, constraints);
   - task: **first** a broad search for sources of the types assigned to the analyst (step 2), **then** studying the code (cite `file:line`) and generating options; don't propose what's already implemented; change nothing;
   - quantity and diversity: **20–40 concrete options**, the full spectrum — from conservative (improve what exists) through notable enhancements to radical (change the approach, architecture, technology), necessarily several unconventional and "what if…" ones; options must not be rephrasings of each other;
   - answer format — one line per option: `option · where · why · code impact (targeted/several modules/architecture) · quality (high/medium/low) · source (number from the source list)`; after the list — sources: `№ · type · title and link · year · how it helps (one phrase)`.

## 2. Broad search and two analysts in parallel

The source search happens **before** idea generation and must be broad: each analyst runs **at least 10–15 web searches** of different types, not 2–3 superficial ones. For each source found, it records the type, year and how it helps with the topic.

**Source type matrix** — split it between the analysts so that together they cover more (skip types irrelevant to the topic; put each analyst's part of the matrix into their brief):

| Source type | Examples | Assigned to |
|---------------|---------|------|
| Scientific papers | Google Scholar, arXiv, ACM DL, IEEE Xplore | Codex |
| Conference talks | GDC Vault, SIGGRAPH, topic-specific conferences | Claude |
| Books | classic and recent books on the topic, chapters, surveys | Codex |
| Documentation and standards | official docs of engines, libraries, platforms, specifications, RFCs | Claude |
| Company engineering blogs | technical blogs of studios and companies, postmortems | Claude |
| Open source | GitHub repositories, issues, PRs, design discussions | Codex |
| Magazines and media | specialized outlets, down to popular ones: Wired, The Verge, Habr, Medium | Claude |
| Forums and Q&A | Stack Overflow, Reddit, Hacker News, specialized forums | Codex |
| Video and podcasts | YouTube talks, breakdowns, podcasts | Claude |

Launch both **in one message**, both in the background.

- **Claude** — `Agent` with `subagent_type: general-purpose`, `run_in_background: true`, `model` and `effort` per the optimum §2 role table (without optimum — `sonnet` `high`), prompt — the brief with its part of the matrix. For a broad topic it may split the search into parts itself.
- **Codex** — launch per the optimum §7 template. Specifics: model `gpt-6-astra`, effort `high`, read-only sandbox, with web search (`--search`), `-C "<project root>"`, `-o "<scratchpad>/frufru-codex.md"`, prompt — the brief with Codex's part of the matrix; read the result from `frufru-codex.md`. Without optimum (the `--search` flag goes **before** `exec`; via `Bash` with `run_in_background: true`, timeout at least 20 minutes):

  ```bash
  codex --search exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high -s read-only     -C "<project root>" -o "<scratchpad>/frufru-codex.md" - < "<scratchpad>/frufru-brief-codex.md"
  ```

  Save the brief for Codex to `frufru-brief-codex.md`.

While the analysts work, don't research the same topic yourself — wait for the completion notifications.

### Fault tolerance

- If Codex isn't found, crashed or returned an empty answer, tell the user once and continue with Claude only (then the «Автор» column says Claude everywhere). If time allows, launch an additional Claude subagent on the source types assigned to Codex.
- If the Claude subagent failed, likewise continue with Codex and, if possible, hand its source types to a second Codex run or a new subagent.
- If both analysts failed, say so and don't invent a table.

## 3. Aggregation

1. **Merge duplicates**: options that are essentially the same become one item with author «Claude + Codex»; take the more precise wording and location, merge the sources. Agreement between two independent analysts is a strong signal; other things being equal, rank such an item higher. Merge identical sources in the lists too.
2. **Verify** each option against the code (read the cited spot): discard false ones, already implemented ones, ones not applicable to the project, and ones referencing nonexistent files, APIs or sources. Don't split one idea into several items, but don't glue different approaches to one problem together either — in fru-fru, alternatives are valuable.
3. **Group by direction** (e.g., «механика», «рендер», «архитектура», «UX») — write the direction at the start of the «Вариант» cell or use row order within groups of the same rating.
4. **Re-rate them yourself**, without copying the analysts' ratings:
   - **Idea quality:** ★★★ high (noticeable benefit, new to the project, backed by sources) · ★★ medium · ★ low (doubtful benefit or weak justification).
   - **Code impact:** 🟢 точечно (one file or function) · 🟡 несколько модулей (new logic, edits in different places) · 🔴 архитектура (rework, risks, new dependencies). If implementation difficulty differs noticeably from the volume of changes (little code but a hard algorithm), note it with a word in the cell, e.g. «🟢 точечно, сложный алгоритм».
5. **Sort**: by quality per unit of impact — ★★★🟢 → ★★★🟡 → ★★🟢 → ★★★🔴 → ★★🟡 → ★🟢 → ★★🔴 → ★🟡 → ★🔴; within a group, «Claude + Codex» goes higher.
6. **Keep all verified options** — don't cut down to 5–15 as in /predlozhi. If the topic allows, there should be at least 20 options; if fewer remain after verification, honestly say why (narrow topic, many discarded).
7. If the analysts contradict each other (one advises X, the other the opposite), keep both options if both are justified; otherwise choose based on the code and sources; briefly note the disagreement in the notes.

## 4. Result (in Russian)

1. One line: the topic, who participated (Claude, Codex, or only one and why), how many sources by type (e.g., «источников 27: 5 статей, 4 доклада, 6 блогов, 3 репозитория, 4 форума, 3 СМИ, 2 видео»).
2. Options table:

| № | Вариант | Где | Зачем | Влияние на код | Качество | Источник | Автор |
|---|---------|-----|-------|----------------|----------|----------|-------|
| 1 | кратко, что сделать | `файл:строка`, модуль или компонент | кратко, какую проблему решает или что даёт | 🟢 точечно | ★★★ | И3, И7 | Claude + Codex |

   Cells — one short phrase each, no line breaks and no `|` inside the text. «Где» — the shortest precise location of the change: `file:line`, file, folder or component (for new code — where it will appear, e.g. «новый `src/sync.ts`»). «Источник» — numbers from the sources table (`И1`, `И2`…) or «—» if the option was devised without relying on a source. «Автор» — `Claude`, `Codex` or `Claude + Codex`.
3. Compact sources table (only those referenced by options or that significantly influenced the analysis):

| № | Тип | Источник (ссылка) | Год | Что дал |
|---|-----|-------------------|-----|---------|
| И1 | статья | [Название](https://…) | 2024 | одна фраза: какую идею или факт дал |

4. Below the tables — 3–5 lines of notes: non-obvious items (`№ — approach`), significant disagreements between analysts, and one line on how many options were discarded during verification and why (e.g., «отброшено 9: 4 уже реализованы, 3 неприменимы, 2 ссылались на несуществующий API»).
5. Models line: `Модели: аналитик Claude — <модель, effort>; Codex — <модель, effort / не запускался>`.
6. Last line: «Скажите номера вариантов — внедрю (например, через /dorabotay)».
