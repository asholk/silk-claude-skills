---
name: razrabotay
description: Development grounded in best practices — first a search for best practices and algorithms for the request (web + current code), then a plan (subagent on the Fable model), plan execution by a subagent, review of the result by a Fable subagent with verification in the main process, and a brief report. Use when the user writes «разработай …», «Разработай», calls /razrabotay, or asks to develop a feature, algorithm, module or system following best practices.
argument-hint: <what to develop>
---

# Razrabotay

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

User request: **$ARGUMENTS**

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it isn't installed, the models are given below.

You are the main process: you research, verify and report. Planning and review are done by subagents on the **Fable** model (use another model only if the user named it explicitly; this rule overrides the `optimum` skill's assignments); an executor subagent writes the code. Don't edit code yourself, not even trivial things: all fixes also go through a subagent.

## 1. Search for best practices and algorithms

1. State the essence of the task: what we're building, constraints (language, framework, platform, performance), success criteria.
2. Orient yourself in the project (2–5 Grep/Glob/Read calls): where the code will live, what conventions, libraries and versions are already used. Don't explore the whole project.
3. Find best practices and algorithms via `WebSearch` (load it via `ToolSearch` if the tool is deferred). Send 2–4 searches in a single response:
   - established algorithms and approaches to the task, their complexity and trade-offs;
   - recommendations from the official documentation of the framework/engine/library in use (account for the version used in the project);
   - common mistakes and pitfalls.
   Open key sources via `WebFetch` when needed. Prefer official documentation and authoritative sources; mind the date — don't use outdated APIs.
4. If the task is purely local and an external search won't add anything (e.g., a rename), skip the web search and say so in one line.
5. Choose an approach: one recommended option and a short rationale for why it beats the alternatives in this project's context.

## 2. Plan (Fable subagent)

Launch the planner: `Agent`, `subagent_type: Plan`, `model: fable`, `effort: high`. The prompt is self-contained: the user's request, the task essence and constraints from item 1, the chosen approach and source links, the project paths and conventions found, decisions from the conversation that must not be broken, and the plan requirements (below); "change nothing, return the full plan in your answer". While it works, don't draft the plan yourself. When you get the plan, verify it: paths and entities exist (Glob/Grep), the steps cover the whole request, verification is feasible. Fix minor inaccuracies yourself. Don't show the full plan to the user unless they asked.

Plan requirements:
- the chosen approach/algorithm and sources (links);
- implementation steps in order: files, classes, functions, what to create and what to change;
- edge cases and errors to handle;
- how to verify: build, tests (which to write/run), manual check;
- what not to touch: decisions from the conversation, existing behavior.

If the request contains a genuine fork that can't be resolved from the code and reasonable defaults, ask one question via `AskUserQuestion` with the recommended option first. Otherwise don't ask; decide yourself.

## 3. Execution in a subagent

1. If the project is a git repository, record the verification baseline: `git status --short` and `git rev-parse HEAD`. During verification, separate changes that existed before work started from the new ones.
2. Launch a subagent: `Agent`, `subagent_type: general-purpose`; `model` and `effort` per the optimum §2 role table (without optimum — `sonnet` `medium`, hard tasks — `opus` `high`). The subagent doesn't see the conversation, so the prompt is self-contained:
   - the user's request and the goal;
   - the best practices found, the chosen algorithm and source links;
   - the full plan;
   - known paths, names, conventions and decisions that must not be broken;
   - the subagent rules (block below) — in full.
3. Tell the user in one line that approach X was chosen and implementation has started. Wait for the completion notification; don't work in parallel yourself and don't invent a result before the notification.

### Subagent rules (paste into the prompt)

> - Follow the plan and the chosen approach. If along the way it turns out the plan is wrong or the approach doesn't fit, deviate minimally and be sure to explain why in the report.
> - Find the relevant code in as few steps as possible: Grep/Glob by keywords, read only the needed fragments.
> - Resolve ambiguity yourself: pick the most reasonable interpretation consistent with the existing code and state it in the report. Don't stop to ask for clarification.
> - Write in the style of the surrounding code: same names, idioms, UI message language and comment density. No refactoring and nothing that wasn't asked for.
> - If the project has tests, add tests for the new logic and the edge cases from the plan.
> - Budget: ~30 calls, including child agents; retry a failed attempt ≤ 2 times, then stop and return a partial report: what's done, what's left, and why.
> - Run the available checks: syntax, build, linter, tests. If something breaks, fix it.
> - Verification: include the command, exit code and outcome.
> - Before building, wait for other builds to finish with the script `~/.claude/skills/optimum/references/wait-builds.ps1` (the "Build" section below); don't kill other processes.
> - Don't commit, don't push, don't delete other people's files.
> - Report: what was done for each plan step, deviations from the plan, list of changed files, how it was verified and what couldn't be verified, assumptions made.

## Build: wait for other builds first

Before every build (yours and a subagent's), wait for other builds with the script `~/.claude/skills/optimum/references/wait-builds.ps1` per optimum §4 "Build": run it in the background `powershell -NoProfile -File "<optimum folder>/references/wait-builds.ps1" [-ExtraNames <project tools>]`; exit 0 — OK to build, 2 — check failed (tell the user), 3 — timeout; don't kill other processes; if the build failed because of a parallel one, wait and retry; Unreal — ask to close the editor of the same project (Live Coding). If the script is missing, check processes with `Get-CimInstance Win32_Process` (UnrealBuildTool, MSBuild, cl, link, ninja, cmake, gradle, etc.). Pass this rule to the subagent together with the script path.

## 4. Verifying the result (Fable review + your verification)

1. Look at the actual changes: `git diff` against the recorded baseline; outside git, read the changed spots in the files from the report. Don't rely on the report alone.
2. Launch the reviewer: `Agent`, `subagent_type: general-purpose`, `model: fable`, `effort: high` — fresh context, no implementation history. In the prompt: the request, the plan, the chosen approach and sources, the baseline (`git diff <baseline>` or the list of changed files), the criteria from item 4, the answer format «критическое/некритическое · файл:строка · проблема · как исправить», one line per finding (or «замечаний нет»), and a ban on changing, building or committing anything.
3. While the reviewer works, rerun the checks yourself (syntax, build, tests) — build only after waiting for other builds.
4. Review criteria (apply them yourself too when going through findings):
   - is the request fully done, and every plan step;
   - is the chosen approach/algorithm implemented correctly and does it match the best practices found;
   - no logic errors, crashes, races, leaks, data loss, vulnerabilities;
   - are the edge cases from the plan handled;
   - no nearby existing behavior broken.
5. Verify every Fable finding against the code; discard false ones. Split the rest into **critical** (bug, crash, data corruption, broken behavior, unfulfilled part of the request or plan, vulnerability) and **non-critical** (style, minor improvements).
6. For critical issues, send them to the same executor subagent via `SendMessage` (otherwise to a new one with full context): `file:line`, what's wrong, a reproduction scenario, the expected behavior. After the fix, re-check the fixed spots — with the same Fable reviewer (`SendMessage`) or a new one with `model: fable`. No more than two rounds; don't hide a remaining critical issue — describe it in the report and suggest what to do.

## 5. Report to the user (in Russian, brief)

- **Подход:** 1–2 lines (plan and review — Fable) — which algorithm/practice was chosen and why, 1–3 key sources as links.
- **Сделано:** 2–5 bullets from the user's point of view; changed files.
- **Проверка:** how it was verified and what wasn't (e.g., «в приложении не запускал»); if there were fixes after verification, one line on what was found and fixed.
- **Модели:** «исполнитель — <модель, effort>; ревью — <модель, effort / не запускалось>».
- Assumptions, deviations from the plan and important non-critical issues — on a separate line, if any.
- Don't retell the process step by step and don't paste code dumps.
