---
name: dorabotay
description: Quick on-request change — a subagent implements it, a separate subagent on the Fable model reviews it, the main process verifies the review findings, sends critical issues back to a subagent for fixing, and briefly reports the outcome. For small edits, new features and fixes in the current project without lengthy planning. Use when the user writes «доработай …», «быстро доработай», calls /dorabotay, or asks to quickly make a specific code change.
argument-hint: <what to change>
---

# Dorabotay

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

User request: **$ARGUMENTS**

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it isn't installed, the models are given below.

You are the main process: you set the task, verify the result and report. A subagent writes the code; a separate subagent on the **Fable** model does the review (use another model only if the user named it explicitly; this rule overrides the `optimum` skill's assignments). Don't edit code yourself, not even trivial things: all fixes also go through a subagent.

## 1. Setting the task

1. If this conversation doesn't yet have the needed context, orient briefly (1–3 Grep/Glob/Read calls): where the affected code lives and what its conventions are. Don't explore the whole project.
2. If the project is a git repository, record the review baseline: `git status --short` and `git rev-parse HEAD`. During review, separate changes that existed before work started from the new ones.
3. Launch a subagent: `Agent`, `subagent_type: general-purpose`, `model: sonnet`, `effort: medium`; for a hard task (algorithms, engine, debugging, performance) — `model: opus`, `effort: high`. The subagent doesn't see the conversation, so the prompt must be self-contained:
   - the user's request and your understanding of exactly what to do;
   - file paths, class and method names known from the conversation; earlier decisions that must not be broken;
   - the subagent rules (block below) — pass them in full.
4. Wait for the completion notification. Don't do the work in parallel yourself and don't invent a result before the notification. Tell the user in one line that the task has been launched.

### Subagent rules (paste into the prompt)

> - Find the relevant code in as few steps as possible: Grep/Glob by keywords, read only the needed fragments.
> - Resolve ambiguity yourself: pick the most reasonable interpretation consistent with the existing code and state it in the report. Don't stop to ask for clarification.
> - Make targeted edits in the style of the surrounding code: same names, idioms, UI message language and comment density. No refactoring and nothing that wasn't asked for.
> - Run the cheapest available check: syntax (`node --check`, `python -m py_compile`, etc.), build, linter or affected tests. If something breaks, fix it.
> - Before building, wait for other builds with the script `~/.claude/skills/optimum/references/wait-builds.ps1` (rules are in the "Build" section below and are passed to you along with the script path); don't kill other processes. If your build failed because of a parallel one (mutex, "concurrent builds", locked files), wait and retry; don't change the code.
> - Budget: ~N calls, including child agents; retry a failed attempt ≤ 2 times, then stop and return a partial report: what's done, what's left, and why.
> - Verification: include the command, exit code and outcome.
> - Don't commit, don't push, don't delete other people's files.
> - Report: what was done, list of changed files, how it was verified and what couldn't be verified, assumptions made.

## Build: wait for other builds first

Before every build (yours and a subagent's), wait for other builds with the script `~/.claude/skills/optimum/references/wait-builds.ps1` per optimum §4 "Build": run it in the background `powershell -NoProfile -File "<optimum folder>/references/wait-builds.ps1" [-ExtraNames <project tools>]`; exit 0 — OK to build, 2 — check failed (tell the user), 3 — timeout; don't kill other processes; if the build failed because of a parallel one, wait and retry; Unreal — ask to close the editor of the same project (Live Coding). If the script is missing, check processes with `Get-CimInstance Win32_Process` (UnrealBuildTool, MSBuild, cl, link, ninja, cmake, gradle, etc.). Pass this rule to the subagent together with the script path.

## 2. Review (Fable subagent + your verification)

1. Look at the actual changes: `git diff` against the recorded baseline. Outside git, read the changed spots in the files from the subagent's report. Don't rely on the report alone.
2. Launch the reviewer: `Agent`, `subagent_type: general-purpose`, `model: fable`, `effort: high` — fresh context, no implementation history. In the prompt: the user's request, the baseline (`git diff <baseline>` or the list of changed files from the report), the criteria from item 4, the answer format «критическое/некритическое · файл:строка · проблема · как исправить», one line per finding (or «замечаний нет»), and a ban on changing, building or committing anything.
3. While the reviewer works, rerun the check yourself (syntax, build or tests). Build only after waiting for other builds (the "Build" section above).
4. Review criteria (apply them yourself too when going through findings):
   - is the request fully done, the way the user would understand it;
   - no logic errors, crashes, races, handler leaks, data loss;
   - no nearby existing behavior broken (clicks, hotkeys, saving, other modes);
   - no name clashes with framework APIs, calls to nonexistent methods, missing `null` checks.
5. Verify every Fable finding against the code; discard false ones. Split the rest:
   - **Critical**: bug, crash, data loss or corruption, broken existing behavior, unfulfilled part of the request, vulnerability.
   - **Non-critical**: style, minor improvements, debatable choices. Don't fix them; only mention them in the summary if they matter to the user.

## 3. Fixes (only for critical issues)

1. Send the issues to the same subagent via `SendMessage` (it keeps its context). If that's unavailable, launch a new one with full context. For each issue give `file:line`, what's wrong, a reproduction scenario and the expected behavior. Repeat the subagent rules.
2. When it finishes, re-review only the fixed spots — with the same Fable reviewer (`SendMessage`) or a new one with `model: fable`.
3. No more than two rounds of fixes. If a critical issue remains, don't hide it: describe it in the summary and suggest what to do.

## 4. Summary for the user (in Russian, brief)

- **All good:** 2–5 bullets on what changed from the user's point of view; changed files; how it was verified and what wasn't (e.g., «в приложении не запускал»).
- **There were fixes:** the same plus one line on what the review found and what was fixed.
- Assumptions made and important non-critical issues — on a separate line, if any.
- Models: «исполнитель — <модель, effort>; ревью — <модель, effort / не запускалось>».
- Don't retell the process step by step and don't paste code dumps.
