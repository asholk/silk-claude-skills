---
name: predlozhi
description: Code analysis and improvement suggestions without changes — determines the topic from the request, hands the analysis in parallel to two independent analysts (a Claude subagent on the Fable model and Codex), verifies and merges their ideas, and outputs a single numbered table with the author, benefit and complexity of each suggestion, sorted from best to worst. Use when the user writes «предложи …», «что можно улучшить», «какие есть идеи по …», calls /predlozhi, or asks for code improvement advice without edits.
argument-hint: <topic or area to improve>
---

# Predlozhi

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

User request: **$ARGUMENTS**

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it isn't installed, the models are given below.

You are the analysis coordinator. The thinking is done by two independent analysts — a Claude subagent on the **Fable** model and Codex; you set their task, verify their ideas and combine everything into one table.

**Change nothing**: don't edit or create project files, don't commit, don't run state-changing commands (package installs, migrations, formatters that write). Only reading, searching, running non-writing checks and writing temporary files to the scratchpad are allowed. Pass the same restriction to both analysts.

## 1. Topic and brief

1. From the request, determine the topic and scope of the analysis: which part of the code, which aspect (UX, performance, reliability, architecture, security, maintainability, new capabilities…). If the request is empty or general, take the project or area discussed most recently in the conversation and formulate the topic yourself. Don't ask clarifying questions — state the topic in one line at the start of your answer.
2. Orient yourself briefly (Glob/Grep, 2–5 calls), only to give the analysts an entry point: root, key folders or files, platform and version, constraints. Don't do deep analysis — that's the analysts' job.
3. Write a **brief** — one text for both analysts:
   - topic and scope, project root, entry points;
   - context from the conversation that isn't in the code (user goals, already rejected ideas, constraints);
   - task: study the code (cite `file:line`), if needed run 2–5 targeted web searches (how mature products and libraries solve it, what the documentation recommends, pitfalls), propose 5–12 concrete, verifiable improvements applicable to this specific project; don't propose what's already implemented; change nothing;
   - answer format — one line per suggestion: `suggestion · where · why · complexity (low/medium/high) · benefit (high/medium/low) · how to implement (one phrase)`, followed by sources as links after the list.

## 2. Two analysts in parallel

Launch both **in one message**, both in the background.

- **Claude** — `Agent` with `subagent_type: general-purpose`, `model: fable`, `effort: high`, `run_in_background: true`, prompt — the brief. Use another model only if the user named it explicitly; this rule overrides the `optimum` skill's assignments. For a broad area it may split the search into parts itself.
- **Codex** — launch per the optimum §7 template. Specifics: model `gpt-6-astra`, effort `high`, sandbox `read-only`, **with** `--search`, `-C "<project root>"`, `-o "<scratchpad>/predlozhi-codex.md"`, prompt — the brief (via stdin). Read the result from `predlozhi-codex.md`.

While the analysts work, don't research the same topic yourself — wait for the completion notifications. If Codex isn't found, crashed, returned an empty answer or hit a limit ("out of credits", "usage limit"), tell the user once and continue with Claude (Fable) only (then the «Автор» column says Claude everywhere). If the Claude subagent failed, likewise continue with Codex.

## 3. Aggregation

1. **Merge duplicates**: suggestions that are essentially the same become one item with author «Claude + Codex»; take the more precise wording and location. Agreement between two independent analysts is a strong signal; other things being equal, rank such an item higher.
2. **Verify** each suggestion against the code (read the cited spot): discard false ones, already implemented ones, ones not applicable to the project, and ones referencing nonexistent files or APIs. Don't split one improvement into several items.
3. **Re-rate them yourself**, without copying the analysts' ratings:
   - **Complexity:** 🟢 низкая (up to an hour, a targeted edit) · 🟡 средняя (several places, new logic) · 🔴 высокая (rework, risks, new dependencies).
   - **Benefit:** ★★★ high (noticeable to the user or removes a real risk) · ★★ medium · ★ low (a nice small touch).
4. **Sort from best to worst**: by benefit per unit of complexity — ★★★🟢 → ★★★🟡 → ★★🟢 → ★★★🔴 → ★★🟡 → ★🟢 → ★★🔴 → ★🟡 → ★🔴; within a group, «Claude + Codex» goes higher. Keep the best 5–15 items.
5. If the analysts contradict each other (one advises X, the other the opposite), choose based on the code and briefly note the disagreement in the notes.

## 4. Result (in Russian)

1. One line: the topic, what was analyzed, who participated (Claude Fable, Codex, or only one and why), whether web searches were made.
2. Table:

| № | Предложение | Где | Зачем | Сложность | Польза | Автор |
|---|-------------|-----|-------|-----------|--------|-------|
| 1 | кратко, что сделать | `файл:строка`, модуль или компонент | кратко, какую проблему решает или что даёт | 🟢 низкая | ★★★ | Claude + Codex |

   Cells — one short phrase each, no line breaks and no `|` inside the text. «Где» — the shortest precise location of the change: `file:line`, file, folder or component (for new code — where it will appear, e.g. «новый `src/sync.ts`»). «Автор» — `Claude`, `Codex` or `Claude + Codex`.
3. Below the table — no more than 3–5 lines of notes: how to implement non-obvious items (`№ — approach`) and significant disagreements between analysts. One line on how many suggestions were discarded during verification and why (e.g., «отброшено 4: 2 уже реализованы, 2 неприменимы»). Web sources, if they influenced the suggestions — briefly, as links.
4. One line: `Модели: аналитик Claude — fable, high; Codex — gpt-6-astra, high / не запускался`.
5. Last line: «Скажите номера пунктов — внедрю (например, через /dorabotay)».
