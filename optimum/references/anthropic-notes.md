# Cost-efficient and effective work with Claude agents (per official Anthropic materials)

Compiled 2026-10-15. References in square brackets point to section 6. Figures and wording come from the sources. Where Anthropic explicitly says "measure on your own data", this is noted.

## 1. Key principles

1. **Start with the simplest solution.** Add complexity only when it pays off. A workflow (a fixed path in code) is cheaper and more predictable than an agent. An agent is needed when the number of steps is not known in advance [S1].
2. **Context is the main resource.** As the window fills, quality drops (context rot). The goal is "the smallest set of high-signal tokens" [S3, S5].
3. **Tokens grow fast in multi-agent systems.** An agent spends about 4× the tokens of chat, a multi-agent system about 15×. On BrowseComp, token volume explains 80% of the variance in quality. Such a setup pays off only on valuable tasks that parallelize well [S2].
4. **Multi-agent setups fit coupled tasks poorly.** These are tasks with shared context and many dependencies, including "most coding tasks" [S2]. Anthropic's measurements: for a single dependent chain or work that fits in one window, a single orchestrator model at reduced effort "won in every measured case" [S8].
5. **Delegation pays off in two cases:** routine work with a long cost tail, and volume that does not fit in one context window [S8].
6. **Tune effort first, then switch models.** «Tuning effort is often a better lever than switching models» [S7]. Add a second model only if the pairing beats the single model's entire quality/cost curve [S8].
7. **Effort affects all output tokens:** thinking, text and tool calls. At low effort there are fewer, shorter calls. `low` is explicitly recommended for simple tasks and subagents [S9]. For Haiku subagents: medium; low — narrow question (1 question, ≤10 calls).
8. **A subagent exists to keep noise out of the main context.** It works in a separate window and returns only the final message. Anthropic suggests a condensed summary of about 1–2K tokens [S3, S10, S14].
9. **A delegation prompt must contain:** the goal, the answer format, hints on tools and sources, task boundaries. Vague prompts lead to duplicated searches and gaps [S2, S13].
10. **Scale effort to complexity.** Simple fact: 1 agent and 3–10 calls. Comparison: 2–4 subagents with 10–15 calls each. Complex research: more than 10 subagents with clearly separated zones [S2].
11. **Run independent calls in parallel.** The lead agent launches 3–5 subagents, each subagent uses 3 or more tools. This cut research time by up to 90% [S2].
12. **The agent must have an executable check:** tests, build, linter, screenshot. «Claude stops when the work looks done.» Demand evidence, not claims of success [S5].
13. **Mandatory things go into hooks, rare ones into skills; keep CLAUDE.md short.** Hooks are deterministic. Skills load on demand. CLAUDE.md takes context in every session; recommended size is up to 200 lines [S5, S6, S14].
14. **Progressive disclosure.** At startup only the skill's `name` and `description` are visible; the SKILL.md body loads on invocation, other files as needed. Scripts execute without entering the context [S11].
15. **Load data on demand (just-in-time).** Store paths and queries, not content. Filter data in code or a hook before it reaches the model: in Anthropic's example usage dropped from 150K to 2K tokens, i.e., by 98.7% [S3, S12, S6].
16. **Tools are the agent's interface (ACI).** You need a few well-designed tools, pagination and filters, `response_format` with concise or detailed values, clear errors. In Claude Code a tool response is capped at 25K tokens by default [S1, S4].
17. **Prompt caching.** Static parts first, in the order tools → system → messages. Any change to the prefix invalidates the cache. TTL — 5 minutes (write ×1.25) or 1 hour (write ×2). Reads cost 0.1× base price (0.05× on Opus 5.5 and Sonnet 5.5, 0.025× on Fable 5.1). Batch API gives a 50% discount [S15, S16].
18. **A fork is cheaper than a fresh subagent** if it needs the same context: it reuses the parent's prompt cache. A fresh subagent starts with a new cache [S10].
19. **Clean the context.** Use `/clear` between unrelated tasks. If corrections failed twice, start over with a better prompt. `/compact <what to keep>` is itself an expensive request, while `/clear` is free [S5, S6].
20. **Start evals small:** 20–50 real tasks. Grade the outcome, not the path. Prefer deterministic graders, use LLM graders where unavoidable, humans for calibration [S2, S17].
21. **Cache in Claude Code.** Subagents run on a 5-minute TTL. Main conversation: 1 hour on a subscription within the plan, 5 minutes with usage credits or an API key. Waiting for background agents longer than the TTL means the orchestrator's next turn runs without cache [S19].
22. **Fable pricing.** Per token about ×2.5 Opus ($10/$50 vs $4/$20), per solved task about ×5: Opus 5.5 at medium roughly equals Fable 5.1 at high in quality on SWE-bench Pro, $0.22 vs $1.19. Depending on the plan/tier, Fable may be billed from usage credits rather than plan limits [S8, S18].
23. **Two passes.** Run a batch of tasks at a cheap level, retry the failed ones at a higher effort or model: per Anthropic about −40 % cost at the same quality. Choose the model by the hardest ~10 % of tasks, not the median. Don't give Haiku context over 100K tokens: it gets more expensive per token [S8].
24. **Fork and built-in subagents.** A fork inherits the conversation context; its `model` and `effort` are ignored (source: the Agent tool description). The built-in Explore under a Fable session runs on Opus on the Anthropic API/subscription (on Bedrock/Vertex/Foundry — the session model). Explore and Plan do not get CLAUDE.md [S10].

## 2. Task type → model and effort

Current lineup (Claude API) [S16, S7]:

| Model | ID | Input / output price per MTok | Default effort | Official purpose |
|---|---|---|---|---|
| Claude Fable 5.1 | `claude-fable-5-1` | $10 / $50 | high | «demanding reasoning and long-horizon agentic work» |
| Claude Opus 5.5 | `claude-opus-5-5` | $4 / $20 | medium | «long-running agentic coding and knowledge work» |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | high in the API; medium in Claude Code | «best combination of speed and intelligence» |
| Claude Haiku 5.5 | `claude-haiku-5-5` | from $0.10 / from $0.50 | medium | «high-volume, latency-sensitive tasks such as classification, extraction, and routing»; in the selection matrix — «sub-agent tasks» |

All models have a 1M window and up to 128K output. On Opus 5.5 and Fable 5.1 thinking is always on. Opus 5.5 is the recommended starting model: «Most workloads start with Claude Opus 5.5» [S7]. Claude Code aliases `haiku`/`sonnet`/`opus` on the Anthropic API point to the 5.5 versions, `fable` to Fable 5.1, and `opusplan` uses Opus in plan mode and Sonnet during execution [S18].

Effort level descriptions in Claude Code [S18]:
- **low** — fast iterations with review of each step;
- **medium** — everyday work with a clear scope;
- **high** — verification matters, edge cases likely (a bug in existing code);
- **xhigh** — deeper but more expensive;
- **max** — hard autonomous tasks, «prone to overthinking».

The table below is inferred from official wording, not a direct Anthropic table. Anthropic everywhere requires validating the choice on your own tasks.

| Task type | Recommendation | Justification |
|---|---|---|
| Code search, reconnaissance | Explore subagent (read-only) or your own subagent with `model: haiku` and effort medium; low — narrow question (1 question, ≤10 calls) | The docs explicitly suggest overriding Explore to `model: haiku`, and setting `haiku` for simple subagent tasks [S10, S6]. `low` — «such as subagents» [S9]. On `low` with long prompts Haiku may skip a search or check [S9] |
| Mechanical data generation, bulk verifiable outputs | Haiku 5.5, effort medium; low — narrow question (1 question, ≤10 calls); for the API — Batch (−50%) | «Haiku 5.5 for high-volume, checkable outputs», but measure first [S8]. Batch [S16]. Fan-out pattern: `claude -p` over a list of files [S5] |
| Writing texts, content | Sonnet 5.5, effort medium/high | Matrix: Sonnet — «content creation», «code generation, data analysis» [S7]. Set the answer length in the prompt: effort does not reliably control it [S9] |
| Ordinary code with a clear spec | Sonnet 5.5 (medium) or Opus 5.5 (medium) | «Sonnet handles most coding tasks well and costs less than Opus» [S6]. For Sonnet 5.5, well-specified agentic tasks — medium, hard ones — high [S9] |
| Complex code, algorithms, debugging | Opus 5.5, effort high/xhigh; if xhigh/max is not enough — Fable 5.1 | high — for bugs in existing code [S18]. xhigh — for tasks longer than 30 minutes [S9]. Escalation to Fable [S7]. Opus 5.5 costs about 1/5 of Fable 5.1 per solved SWE-bench Pro task at statistically similar quality [S8] |
| Architecture, plan | Opus 5.5 (or `opusplan`), plan mode; Fable 5.1 for multi-hour tasks | «Reserve Opus for complex architectural decisions or multi-step reasoning» [S6]. `opusplan` [S18]. Selection matrix [S7] |
| Code review | A separate subagent with fresh context and read-only tools; `/code-review`; model inherit or sonnet, opus for security | Fresh context is not biased toward its own code [S5, S13]. Example security-reviewer with `model: opus` [S5]. Allow the reviewer to flag only correctness and requirements issues [S5] |
| Fact-checking | Code or a deterministic grader where possible; otherwise one LLM call with a rubric (score 0–1 and pass/fail) | A rubric and a single prompt gave the most stable and most human-like scores [S2]. Grader hierarchy [S17] |
| Summarization, classification, extraction | Haiku 5.5, effort medium; low — narrow question (1 question, ≤10 calls) | Haiku's direct purpose [S16]. Compaction: tune for recall first, then precision [S3] |

## 3. Rules for delegating to subagents

**When to delegate** [S10, S13, S2, S8]:
- A side task will produce lots of output that won't be needed later: searching dozens of files, logs, tests, documentation.
- There are several independent directions, e.g., breadth-first research. Explicitly write "can run in parallel".
- A fresh look is needed: review or verification.
- The work exceeds one context window: split it into parts.
- Restrictions are needed: read-only tools, a separate model or effort.

**When not to delegate** [S10, S13, S8]:
- A small task: overhead exceeds the benefit. If the diff fits in one sentence, even a plan is unnecessary [S5].
- A sequential chain with dependencies, or phases with a large shared context.
- Edits to one file by several agents (conflicts).
- Iterative work with frequent clarifications, or when latency matters: a subagent starts from scratch.
- Agents need to talk to each other: subagents can't, that's what agent teams are for (about 7× more tokens in plan mode) [S6].

**What to put in the prompt** [S2, S13, S5]:
- The goal and the "done" criterion.
- Boundaries: what is in scope, what is not, which files and folders.
- Where to look: tools, sources, existing patterns.
- Effort budget: approximate number of calls or files per the scale in item 1.10.
- The exact answer format.
- Absolute paths and concrete names — this prevents a whole class of errors [S1].

**How to reduce returned context:**
- Ask for a summary or conclusions, not raw material: a table, a list of paths with lines, a verdict. Guideline — 1–2K tokens [S3].
- Have the subagent write large artifacts to a file and return only a link [S2].
- Many subagents with detailed reports will overflow the main context [S10].
- Filter long command output with hooks or scripts (FAIL/ERROR only) [S6].

**Parallelism:**
- Launch independent subagents in one message or in the background.
- Default limit — 20 concurrent subagents and 3 nesting levels [S10].
- For parallel code edits use `isolation: worktree` or separate sessions in worktrees [S5, S10].
- Bulk migrations: `/batch` (5–30 subagents in their own worktrees) or a `claude -p` loop with `--allowedTools`. First run on 2–3 files and refine the prompt [S5].

**Subagent model** [S10, S18]:
- Resolution order: call parameter → `model` in frontmatter (`inherit` — session model) → `CLAUDE_CODE_SUBAGENT_MODEL` → main session model.
- `/model` also switches all subagents with `inherit`. To keep a subagent on a cheap model, set `model` explicitly.
- A subagent can have its own `effort`, `maxTurns` and restricted `tools`.

## 4. Quality control while saving

From cheap and reliable checks to expensive ones [S5, S17]:
1. **Deterministic checks:** tests, build, types, linter, comparison with a reference. Fast, cheap, reproducible [S17]. Write a failing test first, then the fix [S5].
2. **Hard gates:** a Stop hook prevents ending the turn until the check passes. A `/goal` condition re-checks it every turn [S5].
3. **Code intelligence plugins** (LSP) for typed languages: type errors are visible right after an edit, without compiling, and with fewer unnecessary file reads [S6].
4. **Evidence instead of claims:** test output, the command and its result, a screenshot [S5].
5. **An independent reviewer subagent** with fresh context sees only the diff and the criteria. Restrict it to correctness and requirements issues, otherwise overengineering begins [S5].
6. **LLM-as-judge:** one call, a rubric, a 0–1 score plus pass/fail. Calibrate against humans and read transcripts [S2, S17].
7. **Eval metrics.** pass@k — one success is enough. pass^k — consistency is needed: at 75% success per attempt, pass^3 ≈ 42% [S17].
8. **If you lower effort or model, rerun the eval.** Tune effort on your own data: settings from older models don't carry over [S9]. Haiku on `low` has a higher risk of a skipped check [S9].

## 5. Anti-patterns

- **A multi-agent setup for a coupled task** or work that fits in one window: 15× more tokens with no gain [S2, S8].
- **A subagent for a trifle** and a "zoo" of narrow agents: most teams settle on a few well-defined agents [S13].
- **"Explore everything" without bounds:** the agent reads hundreds of files (infinite exploration) [S5].
- **Kitchen-sink session:** unrelated tasks in one session, where context is paid for on every turn [S5, S6].
- **Repeated corrections in a polluted context** instead of `/clear` and a new prompt [S5].
- **Bloated CLAUDE.md:** rules get lost, tokens are spent every session [S5, S14].
- **Everything on Opus or Fable with `max` by default.** `max` gives diminishing returns and tends to overthink [S18, S9]. High bills usually come from uncleared sessions and Opus by default [S6].
- **Switching model or tools mid-cached conversation** invalidates the cache. Switching MCP breaks the cache only without tool search (it is on by default, and connecting an MCP doesn't touch the cache). Switching effort doesn't break the cache on API key/subscription (Claude Code, 5.5 models / Fable 5.1); on Bedrock/Vertex and in older versions it invalidates it [S9, S15, S19]. Returning after a pause longer than the TTL also causes a cache miss [S15, S6, S19].
- **Detailed subagent reports in the main context** and raw logs instead of filtered ones [S10, S6].
- **A reviewer obliged to find problems,** and trying to fix every remark, lead to overengineering [S5].
- **"Looks done" without verification:** the trust-then-verify gap [S5].
- **Many unused MCP servers;** when a CLI exists (`gh` etc.), it is cheaper [S6].
- **An advisor/orchestrator pairing "just in case".** In Anthropic's measurements the gain is often within noise, and one pairing was worse than the single model [S8].

## 6. Sources

- S1 · Building effective agents · https://www.anthropic.com/engineering/building-effective-agents · 19.12.2024
- S2 · How we built our multi-agent research system · https://www.anthropic.com/engineering/multi-agent-research-system · 13.06.2025
- S3 · Effective context engineering for AI agents · https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents · 29.09.2025
- S4 · Writing effective tools for agents — with agents · https://www.anthropic.com/engineering/writing-tools-for-agents · 11.09.2025
- S5 · Best practices for Claude Code · https://code.claude.com/docs/en/best-practices (formerly anthropic.com/engineering/claude-code-best-practices) · living documentation, read 15.10.2026
- S6 · Manage costs effectively (Claude Code) · https://code.claude.com/docs/en/costs · read 15.10.2026
- S7 · Choosing the right model · https://platform.claude.com/docs/en/about-claude/models/choosing-a-model · read 15.10.2026
- S8 · Optimizing for cost and intelligence · https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence · read 15.10.2026
- S9 · Effort · https://platform.claude.com/docs/en/build-with-claude/effort · read 15.10.2026
- S10 · Create custom subagents (Claude Code) · https://code.claude.com/docs/en/sub-agents · read 15.10.2026
- S11 · Equipping agents for the real world with Agent Skills · https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills · 16.10.2025 (upd. 18.12.2025)
- S12 · Code execution with MCP · https://www.anthropic.com/engineering/code-execution-with-mcp · 04.11.2025
- S13 · How and when to use subagents in Claude Code · https://claude.com/blog/subagents-in-claude-code · 07.04.2026
- S14 · Steering Claude Code: CLAUDE.md, skills, hooks, subagents · https://claude.com/resources/articles/steering-claude-code-skills-hooks-rules-subagents-and-more · 18.06.2026
- S15 · Prompt caching · https://platform.claude.com/docs/en/build-with-claude/prompt-caching · read 15.10.2026
- S16 · Models overview · https://platform.claude.com/docs/en/models/overview · read 15.10.2026
- S17 · Demystifying evals for AI agents · https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents · 09.01.2026
- S18 · Model configuration (Claude Code) · https://code.claude.com/docs/en/model-config · read 15.10.2026
- S19 · Prompt caching (Claude Code) · https://code.claude.com/docs/en/prompt-caching · read 22.10.2026
