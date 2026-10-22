---
name: staged-development
description: Staged development of a large task — code research (if context is missing), a plan of stages and tasks with context-size estimates (drafted by default by Codex GPT-6-Astra high, otherwise by a Claude subagent on the Fable model; the orchestrator verifies it), parallel implementation of independent tasks by subagents (each task = code plus tests written for it, verified by build only), monitoring every 15 minutes with a progress table and ETA, a commit per task, and after ALL tasks are done — a combined review (by default Codex GPT-6-Astra high, otherwise a Claude subagent on the Fable model) and a full test run, fixes, and final commits with a categorized description. Use when the user asks «поэтапно», «по этапам», «с планом и субагентами», «staged development», invokes /staged-development, or sets a task made of several independent parts that is reasonable to parallelize.
---

# Staged development

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it is not installed, the models are given below.

You are the orchestrator. You research, hand out tasks to subagents, watch over them and commit. **By default Codex does the plan and the review** (GPT-6-Astra, effort high, read-only sandbox); you verify its result and make the decisions. Subagents write the task code; you only fix small things after review yourself and resolve conflicts.

**When not Codex — Fable.** If the user asked to plan or review "without Codex" / "with a Claude model", or if Codex is not found (`which codex`), crashed, returned an empty answer or hit a limit ("out of credits", "usage limit") — the plan and review are done by Claude subagents **on the Fable model**: `Agent` with `model: "fable"`, `effort: "high"` (plan — `subagent_type: "Plan"`, review — `general-purpose`). Do not write the plan or do the review yourself: your role is to verify Fable's result. This rule overrides the model layout of the `optimum` skill. Use a different model only if the user named it explicitly. Tell the user once about switching to the fallback.

**How to run Codex** — per the optimum §7 template. Skill specifics: model `gpt-6-astra`, `model_reasoning_effort=high`, sandbox `read-only`, `-C "<repository root>"`. Plan — with `--search` (before `exec`), `-o "<scratchpad>/plan-codex.md"`; review — without `--search`, `-o "<scratchpad>/review-<group>.md"`. The prompt must be self-contained (Codex does not see this conversation); see phases 1 and 4.

**Before any build — wait for other builds.** Before every build (yours or a subagent's), wait for other builds with the script `~/.claude/skills/optimum/references/wait-builds.ps1` per the rules of optimum §4 "Build": run in the background `powershell -NoProfile -File "<optimum folder>/references/wait-builds.ps1" [-ExtraNames <project tools>]`; exit 0 — safe to build, 2 — check failed (tell the user), 3 — timeout; never kill other processes; if a build failed because of a parallel one — wait and retry; Unreal — ask the user to close the editor of the same project (Live Coding). If the script is missing, check processes with `Get-CimInstance Win32_Process` (UnrealBuildTool, MSBuild, cl, link, ninja, cmake, gradle, etc.). Pass this rule to subagents together with the script path.

The phase order is fixed: **0 Research → 1 Plan → 2 Implementation in waves (+ monitoring): code + tests, verified by build only → 3 Task commit** (after each task) → **4 Final check: review of all tasks and full test run, fixes** (once, when ALL tasks are implemented) → **5 Summary**.

**Main rule of phases 2–4.** Each task writes code **and tests for it**, but tests are **not run** during implementation, and no review is done: a task is verified only by a successful build/compilation (including test files). Review and the test run are a single combined pass after all tasks are done. This way implementers don't wait for each other, the build and test queue doesn't grow, and the reviewer sees the system as a whole.

---

## Phase 0. Research (only if context is missing)

Skip this phase if the code affected by the task has already been read in this conversation and the implementation approach is obvious.

Otherwise:
1. Identify the questions you cannot plan without answering: where the relevant logic lives, what extension points exist, how tests and the build work, what the code conventions are (comment style, naming, message language), whether a similar implementation already exists.
2. Narrow questions (file/symbol known) — search yourself (Grep/Glob/Read). Broad ones — launch several `Explore` subagents **in parallel** (one per independent question, in one message; `model` and `effort` per the role table of optimum §2 (without optimum — `haiku` `medium`)), giving each a concrete question and the expected answer shape (paths, signatures, 5–15 lines of conclusions, not file dumps).
3. If there are implementation alternatives, briefly compare them (1–3 options), pick one and justify it in one line. Ask the user (AskUserQuestion) only if the choice is truly theirs (product behavior, irreversible actions), not a technical one.
4. Record the facts implementers will need: build/test/lint commands, style rules, "dangerous" spots.

## Phase 1. Plan

**By default Codex drafts the plan** (run per the optimum §7 template, see "How to run Codex" above; `-o "<scratchpad>/plan-codex.md"`). Prompt for Codex:
- the user's task verbatim and context from the conversation that is not in the code (goals, constraints, rejected options);
- facts from phase 0: key files, build/test commands, conventions, dangerous spots, the chosen implementation option;
- plan requirements — everything from the "Structure", "Context size" and "Entity overlaps" sections below (task fields, S/M/L scale, overlap rule, waves);
- response format — markdown: a task table with the fields from "Structure", then the breakdown into waves, then risks and open questions;
- "change nothing".

While Codex (or Fable) is planning, do not draft a plan in parallel yourself — wait for the result. Then **verify the plan**: paths and entities exist (Glob/Grep), there really are no overlaps of "Entities" within a wave, dependencies are not cyclic, context estimates are plausible, each task's goal is verifiable. Fix what you find yourself (briefly note what you changed relative to Codex). If Codex is unavailable or the user asked, the plan is drafted by a Fable subagent (`Agent`, `subagent_type: "Plan"`, `model: "fable"`, `effort: "high"`) with the same prompt, with `-o` replaced by "return the whole plan in your answer"; verify it the same way.

Save the final plan to a file (the session scratchpad folder, otherwise `.claude/plans/<slug>.md` in the repository — do not commit it). Show the user a short version (the task table) and **continue without waiting**, unless the user asked to approve the plan.

### Structure
- **Stages** — logical milestones (e.g. «Модель данных», «UI», «Интеграция»). Stage N+1 starts after stage N finishes only if it depends on it.
- **Tasks** within a stage — the unit of work of one subagent and one commit.

For each task specify:

| Field | What to write |
|---|---|
| ID | `S1.T2` |
| Goal | what must work after the task, verifiably |
| Entities | files / modules / classes / public APIs the task **changes** (creates, edits, deletes) |
| Reads | what only needs to be read |
| Depends on | IDs of tasks whose result is needed |
| Context | size estimate (see below) |
| Verification | which tests the task **writes** (files, scenarios) and which build confirms that the code and tests compile; tests are run in phase 4 |
| Time estimate | minutes (for ETA) |

### Context size — estimate it yourself
For each task, estimate how much code the implementer must keep in mind: the number and size of files to read (≈ 1 token per 3–4 characters; lines × ~10 tokens), plus the size of the changes.
- **S** (< 20k tokens): 1–3 small files — one subagent, default model.
- **M** (20–60k): several modules — one subagent; list the exact files and fragments (lines) in the prompt so it doesn't read extra.
- **L** (60–120k): split the task into subtasks; if it can't be split — one subagent with a strict file list.
- **> 120k**: must be split.
Estimate the stage as a whole the same way: if the total context of a stage is large, parallel subagents are preferable to a single agent.

### Entity overlaps
Two tasks **overlap** if their "Entities" sets share a file (or one changes a public API the other uses). Put overlapping tasks in different waves (sequentially) or merge them into one task. Shared "bottlenecks" (registries, index files, `package.json`, shared CSS, a main class thousands of lines long) go into a separate short integration task at the end of the stage, not edits from several tasks at once.

## Phase 2. Implementation in waves

1. Split the stage's tasks into **waves**: a wave contains tasks with no entity overlaps and with satisfied dependencies.
2. Launch the wave's tasks **in parallel** — several `Agent` calls in one message (`subagent_type: "general-purpose"`; `model` and `effort` per the role table of optimum §2 (without optimum — `sonnet` `medium`, complex — `opus` `high`)). If the wave's tasks may still touch shared files indirectly (code generation, formatter) and the repository is git, use `isolation: "worktree"` and then merge the changes yourself.
3. **The subagent prompt** must be self-contained (it does not see this conversation):
   - the task goal and the definition of done;
   - the exact list of files it **may change**, and a ban on touching the rest (especially entities of other tasks in the wave);
   - what to read (paths and, where possible, lines);
   - project conventions from phase 0 (style, message language, comments like in the surrounding code);
   - **write tests** for the implemented code (scenarios from the plan's "Verification" field) in the project's style, but **do not run them** and do no review;
   - verification — build/compilation only (code and test files must compile; types/lint — if fast); attach the result;
   - before building — wait for other builds (insert the "Before any build" rule into the prompt together with the path to `wait-builds.ps1`); if the wave's tasks build the same project, subagents do not build — the orchestrator builds after the wave; do not fix errors in files of neighboring wave tasks, list them instead;
   - **do not commit** (the orchestrator commits) and do not start long-running/interactive processes;
   - budget: ~N calls, including child agents; retry a failed attempt ≤ 2 times, then stop and return a partial report: what's done, what's left, why;
   - verification: attach the command, exit code and outcome;
   - report format: changed files (test files separately), what was done (3–7 points), build result, a "For the test phase" section (what the tests check, fragile spots, where expectations may need adjusting), open questions and what needs to be done in other tasks' files.
4. Record each task's start time (for ETA and monitoring).
5. When a subagent completion notification arrives, check that the build passed and the tests were written, then immediately go to phase 3 (commit) for that task, without waiting for the rest of the wave. Launch the next wave as soon as its dependencies are freed. Collect a task's requirements on other files ("wire it up in …") into a shared notes file next to the plan and pass them to the owners/the integration task.
6. If a subagent reported a problem or ran out of budget, give a clarification via `SendMessage` to the same agent (context is preserved) or relaunch with a corrected prompt. Never invent the result of an unfinished agent.

### Monitoring (every 15 minutes)

Right after launching the first wave, set up a periodic check:
- Load `CronCreate` (via `ToolSearch`, `select:CronCreate,CronDelete,CronList`) and create a job with schedule `*/15 * * * *` and the prompt "staged-development monitoring: check subagent liveness and report on the plan <path to plan>".
- If `CronCreate` is unavailable, use `Monitor` (if present) with a 15-minute period; if that is also missing, give a report on each subagent completion notification and warn the user that there will be no periodic reports.

On each trigger:
1. **Liveness:** `ListAgents` / background task statuses. An agent is "alive" if it is working; "stuck" if there have been no new events for longer than 2× its time estimate — then message it via `SendMessage` (status request) or relaunch the task, and note this in the report.
2. **Report to the user** — a short table and a summary line:

```
| Задача | Агент | Статус | Прошло | ETA задачи |
|---|---|---|---|---|
| S1.T1 Модель данных | impl-a | ✅ готово, закоммичено | 12 мин | — |
| S1.T2 API | impl-b | 🔄 в работе | 18 мин | ~10:42 |
| S1.T3 UI | — | ⏳ ждёт S1.T2 | — | ~11:05 |
| S2.T1 Интеграция | — | ⏳ этап 2 | — | ~11:30 |

Готово 1/4 · ревью/исправления: 0 · проблемы: нет · **общее окончание ≈ 11:30**
```

   Statuses: ⏳ ждёт · 🔄 в работе · 🔍 ревью · 🛠 исправления · ✅ готово · ⚠️ проблема / завис.
3. **ETA:** for a task in progress — start + estimate × factor. Factor = (actual time of completed tasks) / (their estimate), starting at 1.0. For waiting tasks — the readiness time of their dependencies + their estimate × factor (+ ~10 % for the commit). Overall finish — the maximum ETA of the last stage plus the final-check estimate (review and tests, usually 20–40 % of the total implementation time). Give absolute local time (`date`) and "≈".
4. When all tasks are finished, delete the monitoring job (`CronDelete`).

## Phase 3. Commit (after each task)

1. Only if this is a git repository. If the current branch is the main one (`main`/`master`/default) and the user did not say to commit directly to it, create a `feature/<slug>` branch once at the start.
2. Add **only this task's files** (`git add <paths>`), not `git add -A`: parallel tasks and other changes in the working tree must not get into the commit. Check `git diff --cached --stat` before committing.
3. Do not skip hooks (`--no-verify` is forbidden). If a hook fails, fix the cause and create the commit again.
4. Message — a Conventional Commits style header and a categorized body. Language — as in the repository history (Russian by default):

   ```
   feat(scope): кратко, что появилось — до ~72 символов

   ✨ Добавлено
   - …
   🐛 Исправлено
   - …
   ♻️ Переработано
   - …
   ⚡ Производительность
   - …
   🧪 Тесты
   - …
   📝 Документация
   - …

   Задача: S1.T2 · План: <Codex GPT-6-Astra high / Claude Fable> · Тесты написаны, не запускались; ревью — в финальной проверке
   ```

   Header type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`, `build`. Omit empty categories. Each item is one line, about the substance of the change, without listing files. At the end — attribution lines, if the session's system instruction requires them.
5. Pass the message via heredoc (`git commit -F - <<'EOF' … EOF`) so quotes and line breaks don't break. Push only if the user asked.
6. Not git (Perforce, etc.) or the VCS is not available from the console — do not commit; at the end prepare a changelist description (same format, with a note on the state of tests and review) and a list of files for add/checkout, and tell the user.

## Phase 4. Final check: review and tests (after ALL tasks are done)

Start only when all plan tasks are implemented, committed, and the full build passes.

1. **Full build** (after waiting for other builds) — green, with no new warnings.
2. **Review — one combined pass over all tasks, in parallel.** Split the changes into 3–8 groups by area (e.g. by stage or subsystem) and run the group reviews simultaneously. The default reviewer is Codex (run per the optimum §7 template, see "How to run Codex" above; without `--search`, `-o "<scratchpad>/review-<group>.md"`). Prompt:

   ```
   Do a code review of the changes in <group>: <goals of the group's tasks>.
   Diff: git diff <base>..HEAD -- <files> (or files: <list>, if not git); read the surrounding code if needed.
   Report only what matters: bugs, edge cases, regressions, seams between tasks, security, mismatch with the goal, project style, gaps in tests. No matters of taste.
   Format: "severity · file:line · problem · how to fix", one line per finding; if there are no findings — "no findings".
   Change nothing.
   ```

   **Fallback reviewer** — if Codex is unavailable (not found, crashed, empty answer, out of credits/limit — "out of credits", "usage limit") or the user asked for a review without Codex: fresh `general-purpose` subagents with `model: "fable"`, `effort: "high"` (a different model only if the user named it explicitly), without the implementation history, same prompt; all groups in one message, in parallel. The repeat review round in step 5 uses the same reviewer.
3. **Run all tests** — in parallel with the review or right after it (it doesn't interfere with reviewers' builds: the review builds nothing). Run the project's full test suite, collect results with numbers (passed/failed/skipped) and failure texts.
4. **Triage and fixes.** Verify review findings and test failures yourself (read the code): discard false ones with a note; classify each test failure as "implementation bug" or "wrong test expectation". Hand fixes out to subagents by file area (no overlaps, in waves as in phase 2); fix small things yourself. Each fixer rebuilds and runs the tests of its area.
5. **Repeat.** Full build and full test run; after substantial fixes — a short repeat review round covering only them. At most 2 rounds; move whatever remains into the summary as known limitations.
6. **Fix commits** — per the phase 3 rules, type `fix`/`test`, with the note «Финальная проверка · ревью: <Codex GPT-6-Astra high / Claude Fable>, замечаний исправлено: N · тесты: X/Y».

## Phase 5. Summary

When all stages are closed:
- final task table (status, commit `short sha`, actual/estimated time);
- overall result of the final check (build; tests — with real numbers; number of review findings found/fixed/discarded);
- what was not done or deferred (with the reason), problems found but not fixed;
- whether the monitoring job was deleted;
- `Модели: исполнитель — <модель, effort>; план — <модель, effort>; ревью — <модель, effort / не запускалось>; Codex — <модель, effort / не запускался>`.

Be brief; the user reads the outcome, not the process.

## Rules

- Do not run tasks that change the same file in parallel. If in doubt about an overlap — run sequentially.
- In phase 2 tests are only written; running tests and review happen only in phase 4, after all tasks.
- Builds are incremental: if code is copied to a separate build location, preserve file timestamps (`cp -p`/`rsync -t`), otherwise every build becomes a full one.
- No build while another one is running on the system: wait first (see "Before any build"), then build.
- Never invent subagent statuses or results: "still running" means still running.
- Do not expand the scope beyond the plan; new findings go into the summary or a separate task with the user's consent.
- Destructive actions (deleting user files, `reset --hard`, force-push, data migrations) — only with the user's confirmation.
- If the task is small (one or two files, < 30 minutes), say the staged process is overkill and do it directly, unless the user insists.
