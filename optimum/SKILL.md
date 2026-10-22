---
name: optimum
description: Optimum — rules for cost-efficient, high-quality task execution by Claude agents, based on Anthropic's recommendations - choosing model and effort (Haiku / Sonnet / Opus / Fable), when to delegate to subagents, Codex or fork, a prompt template, caching, cheap quality checks. Use when the user writes «оптимум», «экономно», «оптимально», «оптимизированно», «эффективно и качественно», «сэкономь токены», «дешевле», «бюджет», «кэш», «какую модель», «какой effort», invokes /optimum, asks to choose models for subagents or to cut usage; also as an add-on to orchestrating skills (staged-development, fru-fru, razrabotay, dorabotay, predlozhi, concept) whenever any subagents are launched. Not for optimizing the performance of the application itself.
---

# Optimum

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

Goal: minimize **cost per successfully completed task**, not per request — a cheap agent that needs rework costs more. Use the free levers first (context, prompt, parallelism, checks), then effort, and only then switch models. Details and sources — `references/anthropic-notes.md` (read only when you need justification).

## 1. First — is an agent needed at all

- The task fits in one sentence, touches 1–2 files, the file/symbol is known → do it yourself, no subagent and no plan.
- A sequential chain with shared context, edits to one file, frequent clarifications → one executor (yourself or one subagent), not a swarm.
- Delegate when: (a) side work would generate a lot of output useless to the main context (search, logs, reading docs); (b) there are **independent** parts that can run in parallel; (c) a fresh look is needed (review, verification); (d) the volume does not fit in one window.
- Multi-agent work costs ~×15 the tokens of chat — justified only for valuable, well-parallelizable work.
- Need an independent opinion or to save Claude limits → Codex (§7).
- Fresh agent / continuation / fork: independent review — fresh agent; related fixes — continue the same agent (`SendMessage`); work needs the conversation history — `subagent_type: "fork"` (cheaper thanks to the shared cache, but `model`/`effort` are ignored; parallel forks on the same files — only with `isolation: "worktree"`).

## 2. Model and effort by task type

`Agent` parameters: `model` (`haiku` | `sonnet` | `opus` | `fable`) and `effort` (`low` | `medium` | `high` | `xhigh` | `max`). This skill **explicitly authorizes** setting `effort` per the table. Set `model` on **every** call: without it the session model is used (often Fable), and the built-in Explore under a Fable session on the Anthropic API/subscription runs on Opus.

| Task type | model | effort | Why |
|---|---|---|---|
| Code reconnaissance, finding files/symbols, "where is it" | `haiku` (Explore) | medium (low — narrow question) | read-only, answer is paths and conclusions; low — only for 1 question and ≤10 calls |
| Mechanics: bulk verifiable transformations, generating data from a sample, renames, collecting lists, formatting | `haiku` | medium | high-volume and verifiable by a validator/test |
| Summarization, classification, extraction from documents | `haiku` | medium | Haiku's direct purpose |
| Texts, articles, documentation, content | `sonnet` | high | Sonnet — content creation; text quality matters more than price |
| Ordinary code from a clear spec, layout, integration, tests | `sonnet` | medium | «Sonnet handles most coding tasks well and costs less than Opus» |
| Complex code: algorithms, graphics/shaders, engines, debugging, performance | `opus` | high | high — for edge cases and bugs; xhigh — for tasks > 30 min |
| Architecture, plan, API, decision forks | `opus` | high | «Reserve Opus for complex architectural decisions» |
| Code review | `opus` (correctness/security) or `sonnet` (style, simple diffs) | medium–high | fresh context, read-only; correctness and requirements only |
| Plan and review inside `staged-development`, `razrabotay`, `dorabotay`, the Claude analyst in `predlozhi` (when Claude does the work, not Codex) | `fable` | high | user requirement; overrides the rows above |
| Fact-checking, LLM-as-judge | `sonnet` | medium | one call with a rubric: score 0–1 + pass/fail |
| Opus on xhigh failed / multi-hour autonomous task | `fable` | high | escalate only after an actual failure; Fable ≈ ×2.5 Opus per token, ≈ ×5 per task |

Roles in orchestrating skills (`model` and `effort` come from here unless the skill sets them):

| Role | model | effort |
|---|---|---|
| Code executor (`dorabotay` / `razrabotay` / `staged-development`) from a clear spec | `sonnet` | medium |
| Code executor, complex task | `opus` | high |
| Researchers in `fru-fru` / `concept` (Claude subagent) | `sonnet` | high |
| Explore in phase 0 | `haiku` | medium |
| Plan, review, `predlozhi` analyst | `fable` | high |

Priority: explicit user choice > the specific skill's rule > optimum tables > session model.

Rules:
- **Effort before model, but diagnose first.** Missing context → refine the prompt/context; missing thoroughness → raise effort; missing model capability → switch model. If the result is excessive/slow — lower effort first.
- **Two passes:** run a batch of tasks at a cheap level, retry the failed ones at a higher effort/model (per Anthropic ≈ −40 % at the same quality). Pick the level by the hardest ~10 % of tasks, not the median.
- `max` — almost never (diminishing returns, "overthinking").
- Haiku: `medium` by default; `low` may skip verification — put an executable check in the prompt. Don't give Haiku context > 100K tokens (more expensive per token).
- `fable` outside the "Plan and review…" row — only with explicit justification. Fable: ≈ ×2.5 Opus per token ($10/$50 vs $4/$20), ≈ ×5 per solved task (Opus medium ≈ Fable high in quality); depending on the plan it may be billed from usage credits rather than plan limits.

## 3. Delegation prompt (template)

A fresh subagent does not see the conversation. Keep the prompt short but complete:

```
Goal: <what must work/be done> · Done criterion: <verifiable>.
Context: <2–5 lines not in the code; absolute paths>.
May change: <exact list of files>. Do not touch: <everything else / neighbors' files>.
Read: <files and lines>; do not read whole: <large files>.
Budget: ~<N> tool calls / <N> files, including child agents; retry a failed attempt ≤ 2 times, then stop and return a partial report: what is done, what remains, why. Exhausting the budget is not "done".
Check: <command: build/validator/audit>; attach the command, exit code and summary (errors only).
Answer: ≤ <15–40> lines — files, what was done, check result, open questions. Large artifacts — to the specified file if writing is allowed; if read-only — the full result in the message (may exceed the limit).
```

- Shared long rules (contracts, style) go **into a brief file**, and the prompt links to it: prompts stay short, and each agent reads the brief once.
- Don't duplicate work: if a search is delegated to an agent, don't repeat it yourself.
- Scale: simple fact — 1 agent, 3–10 calls; comparison — 2–4 agents; large work — many agents with non-overlapping zones.
- Nesting — one level: a subagent does not spawn its own unless stated. Explore/Plan do not get CLAUDE.md — repeat the needed project conventions in the prompt.

## 4. Parallelism and orchestrator context

- Independent agents — in one message, in the background. Tasks are independent only if there is no shared file, no shared contract/public API and no shared resource (one build, one DB, one port); otherwise — sequentially or `isolation: "worktree"` (it does not remove contention for builds and DBs). Give integration and the shared build to a single executor.
- Limit simultaneously active agents (guideline ≤ 12–16) to avoid hitting limits and flooding your context with reports.
- Don't read agent transcripts; verify the result by facts (git diff --stat, validator, test), not by their words.
- Filter long command output (`| tail`, `grep -E "FAIL|ERROR"`), but keep the command, exit code and check summary: empty filtered output does not prove success.
- Generate data files with a script rather than writing them line by line in context, if it is mechanical.

**Build** — before any build, wait for other builds with the script `references/wait-builds.ps1` (path relative to the skill folder, usually `~/.claude/skills/optimum/references/wait-builds.ps1`). Run in the background (`run_in_background`, timeout up to 60 min): `powershell -NoProfile -File "<optimum folder>/references/wait-builds.ps1" [-ExtraNames node,cargo]`.
- exit 0 — no builds, start yours; 2 — processes could not be checked (do not treat as "no builds", tell the user); 3 — timeout.
- Don't kill other processes. If your build failed because of a parallel one — wait and retry, don't change the code.
- Unreal: only an open editor of the same project (Live Coding) interferes — ask the user to close it.
- Script unavailable — check processes manually: `Get-CimInstance Win32_Process` by the same names.

**Cache** (keep the orchestrator context small):
- Subagents have a 5-min cache TTL. The main conversation — 1 h on a subscription within the plan, 5 min with usage credits or an API key.
- Waiting for background agents longer than the TTL → the orchestrator's next turn runs without cache.
- Changing the model or tool set breaks the cache; changing MCP — only without tool search. Changing effort on 5.5 models / Fable 5.1 does not break the cache (on API key/subscription).

## 5. Quality while saving — from cheap to expensive

1. Deterministic checks: build, `node --check`, validator, tests, audit, comparison with a reference.
2. Evidence, not claims: the agent attaches the check output (errors/summary only).
3. Visual results — a screenshot/PNG the agent opens and evaluates itself.
4. An independent reviewer with fresh context and a narrow mandate (correctness and requirements, no matters of taste).
5. LLM-judge with a rubric — only where there is no deterministic check.
When lowering model/effort — test on 2–3 tasks before rolling out to all.

## 6. Anti-patterns

- A subagent for a trifle; a "zoo" of narrow agents.
- "Explore everything" without bounds and budget.
- Everything on Opus/Fable by default; `max` by default; `fable` without justification outside the plan/review row (≈ ×5 per task).
- Detailed agent reports and raw logs in the main context.
- A reviewer obliged to "find problems"; fixing every remark.
- "Looks done" without verification.
- Repeated corrections in a polluted context instead of a new clear prompt.

## 7. Codex as a second executor

- Choose Codex over a Claude subagent when you need an independent opinion or must not spend Claude limits. Ask both the same question only if independence is needed.
- Analysis/review — always `-s read-only` and `-o <file>`; read only the final result from the file. `--search` is a top-level flag and goes **before** `exec`.
- `model_reasoning_effort` (`low` / `medium` / `high` / `xhigh`) — per the §2 table.
- Run via `Bash` with `run_in_background: true`, timeout ≥ 20 min.
- Not found, crashed, empty answer or limit hit — say so once; if a Claude subagent for the same task is already running — continue with it, otherwise launch a subagent with the role's model: plan/review/analyst — `fable` `high`, others — per the §2 role table.

```bash
codex --search exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high -s read-only \
  -C "<project root>" -o "<scratchpad>/<file>.md" - <<'EOF'
<prompt>
EOF
```

## How to apply

Before every subagent launch (including inside other skills), run through: is an agent needed (§1; Claude, Codex or fork) → task type → `model` + `effort` (§2) → prompt per the template and a short answer (§3) → which cheap check will confirm the result (§5). For large launches, state the model layout in one line of the report to the user (in Russian, e.g., «статьи — Sonnet high, демо — Opus high, разведка — Haiku medium»).
