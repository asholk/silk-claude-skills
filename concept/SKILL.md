---
name: concept
description: Concept — on request, runs two independent researchers in parallel in the background (a Claude subagent and Codex) to find best practices and ideas, distills the best into three distinct offers, and builds a separate minimalist site in the Concept folder — a comparison home page and three landing pages with a short essence, SVG diagrams and illustrations generated via Codex. Use when the user writes «Концепт …», «концепт», «сделай концепт», calls /concept, or asks for concepts, options or landing pages for an idea, product, service or feature.
argument-hint: <idea, product or task for the concept>
---

# Concept

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

User request: **$ARGUMENTS**

> When launching subagents and Codex, follow the `optimum` skill (§2 models, §3 prompt, §7 Codex); if it is not installed, the models are given below.

You are the coordinator. Two independent researchers look for ideas — a Claude subagent and Codex. You set the task, pick the best, form three offers, order the illustrations and build the site yourself.

Skill files:
- `design.md` — design reference: offer skeleton, landing page structure, diagrams, image prompts, style. **Read it before step 3.**
- `gen_images.py` — image generation via Codex (built-in image_gen).

Skill folder path: `~/.claude/skills/concept/` (on Windows `C:\Users\<user>\.claude\skills\concept\`).

## 1. Topic and brief

1. From the request, determine the **subject of the concept** (product, service, feature, business idea, event…), the audience and the goal. If the request is empty, take whatever was discussed last in the conversation. Do not ask clarifying questions: state the topic in one line at the start of your reply.
2. If the concept is about the current project, orient yourself briefly (Glob/Grep, 2–5 calls) so you can pass context to the researchers.
3. Pick a **slug** — a short Latin kebab-case name. Site folder: `<working folder>/Concept/<slug>/`. If it exists, add a suffix `-2`, `-3`…; do not overwrite existing files.
4. Write a **brief** — one text for both researchers — and save it to `<scratchpad>/concept-brief.md`:
   - subject, audience, goal, constraints, context from the conversation; everything the user explicitly asked to take into account (technologies, platforms, partners) goes in a separate mandatory item;
   - task: 4–8 targeted web searches — best practices, market leaders' solutions, successful cases, research, typical mistakes; on that basis, **3–5 fundamentally different concepts** (different approaches, audiences, models, not variations of one);
   - for each concept: name · positioning by the formula "For [who], who has [pain], [name] is a [category] that [benefit]. Unlike [alternative], [difference]" · job story "When…, I want…, so that…" · 3–5 key capabilities · reason to believe (why it will work) · why now · alternatives and how it differs from them · model (price, format) · main risk and what to test first · signature idea · 2–3 usage scenes (who, where, what they do — for illustrations);
   - for each concept — a difference passport per §3a: mechanism, interaction scenario, result format, way of delivering value, and the deliberate trade-off;
   - separately — 5–10 best practices useful for any option;
   - confirm real capabilities and limits of the named technologies with documentation; mark anything unconfirmed as "verify";
   - sources as links; do not create or change any files.

## 2. Two researchers in parallel, in the background

Launch both **in one message**, both in the background.

- **Claude** — `Agent` with `subagent_type: general-purpose`, `run_in_background: true`, `model` and `effort` per the role table in optimum §2 (without optimum — `sonnet` `high`); prompt: read the brief from the file and carry it out, web search via `ToolSearch "select:WebSearch,WebFetch"`.
- **Codex** — GPT-6-Astra, effort high, read-only, with web search; launch per the optimum §7 template if it is installed. Standalone command (the `--search` flag is top-level and goes **before** `exec`; via `Bash` with `run_in_background: true`, timeout at least 20 minutes):

  ```bash
  S="<scratchpad>"
  codex --search exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high -s read-only -C "<working folder>" -o "$S/concept-codex.md" - < "$S/concept-brief.md" > "$S/concept-codex.log" 2>&1
  ```

  Prompt — the brief `concept-brief.md`; result — `concept-codex.md`.

Briefly tell the user the research has started and wait for the notifications — do not research the same topic yourself. If Codex is not found, crashes or returns an empty answer, say so once and continue with Claude; if the subagent fails, continue with Codex.

## 3. Synthesis: three offers

Read `design.md`.

1. Merge both researchers' concepts; treat ideas with the same mechanics as one group and keep one representative. Agreement is not independent evidence of quality. Drop weak, unrealistic and indistinguishable ones.
2. Form **exactly 3 offers** that pass the §3a check. Labels like "proven / bold / niche" do not prove a difference. Shared quality practices may be carried over; carrying over distinctive features requires re-running the pairwise check, so the options don't collapse into one feature set.
3. For each, fill in the **skeleton** from `design.md` §1 (positioning, headline up to 10 words, subheadline, job story, insight, 3 benefits, RTB, why now, alternatives, risk and what to test, model) and the landing section content from §2. Run the 5-second test on every hero.
4. Pick 2–3 diagram types from §3 for each landing — different for different offers, chosen by meaning (a wearable gets "before/after", a system with participants gets an ecosystem, a ritual gets a day timeline).
5. For the home page: 1–5 scores on the same 4–5 criteria, the 2×2 matrix axes, a recommendation, the idea's source (Claude / Codex / Claude + Codex).
6. Write texts in the language of the request, concretely: scenes, numbers, verbs; no "innovative platform" and no "Lorem ipsum".

## 3a. Mandatory difference check before design

The three concepts are independent ways to solve the original problem. Different names, colors, wording, prices and feature counts do not by themselves count as a difference. "Basic / extended / premium" of one solution are pricing tiers, not different concepts.

1. Fix the common goal and the user's non-negotiable requirements. Choose 3–5 free substantive axes: solution mechanism; interaction scenario and role allocation; result format; way of delivering value; required infrastructure. Change the audience only if the user did not fix it. Do not count two consequences of the same change as independent axes.
2. Build an "axis → option 1 / option 2 / option 3" table with concrete decisions. Every pair **1–2, 1–3, 2–3** must differ on at least two independent axes, and at least one of them must be the solution mechanism or the main interaction scenario. Explain the observable consequence: what the user or the system actually does differently. Three complementary modules of one product do not replace three independent solutions.
3. For each option state the distinctive mechanic, a concrete scenario, the deliberate trade-off, and the situation in which it would be preferred over the other two. All options must be viable within the brief: do not add a deliberately weak one for contrast. Different price or speed numbers without a different solution design do not pass.
4. No-names test: strip branding, evaluative adjectives, prices and styling. If the same sequence of actions with the same mechanics remains, they are duplicates. Transfer test: if the key scenario and the explanatory diagram can be moved to a neighboring option by simply swapping names, a substantive difference has not been shown yet.
5. If even one pair fails, rework or replace the duplicating option along a free axis and recheck all pairs. Do not order illustrations or build landing pages until the check passes. At most two rework rounds. If the constraints leave no room for three independent solutions, deliver only the options that passed, explain the constraint and say which requirement would need to be relaxed. Do not violate the brief for the sake of variety. This is an exception to the "exactly 3" and "9 images" requirements: the number of landing pages, comparison rows and illustration sets matches the actual number of options.
6. On the home page show a compact difference table and one sentence on the decisive difference of each pair. The 1–5 quality scores do not replace it. After preparing texts, diagrams and scenes, repeat the tests: styling and carrying over best practices must not erase the differences.

Example of a defect: three planners with the same manual task list, different names and a different number of reminders. Possible distinct mechanics: manual day planning; automatic distribution of tasks into free time slots; participants negotiating tasks through a shared queue. Such a set fits only if each approach solves the original problem within the brief; the differences are confirmed by scenarios and trade-offs, not by names.

## 4. Illustrations via Codex (in the background)

Right after synthesis, **before** building pages:

1. Define the site palette (background, text, 3 offer accents) and write a **style block** per `design.md` §4 — one for the whole concept, palette matching the CSS tokens. Describe characters once and repeat them verbatim.
2. Write `<scratchpad>/concept-images.json`:

   ```json
   {
     "style": "Minimal flat editorial illustration, ... palette: warm off-white #fbfaf7, charcoal #1d1c1a, orange #d9692b, teal #2f7d6d, indigo #4a5bd4 ...",
     "avoid": "text, letters, numbers, logos, watermarks, brand names, photorealism, stock-photo look, clutter",
     "images": [
       {"name": "offer-1-hero",    "aspect": "16:9", "prompt": "..."},
       {"name": "offer-1-scene-1", "aspect": "4:3",  "prompt": "..."},
       {"name": "offer-1-scene-2", "aspect": "4:3",  "prompt": "..."}
     ]
   }
   ```

   9 images: a hero + 2 scenes per offer. Each option gets its own action, key object and composition that explain its mechanic from §3a; changing the accent color is not enough. Keep the shared art style. Prompts in English, one idea each, no text in the image and no brand names.
3. Launch in the background (`Bash`, `run_in_background: true`, timeout 40 minutes; 2 images in parallel, one takes ≈1 minute):

   ```bash
   python -I ~/.claude/skills/concept/gen_images.py "<scratchpad>/concept-images.json" \
     --out "<site folder>/img" --work "<scratchpad>/concept-img-work"
   ```

   Flags: `--only name1,name2` — regenerate selected ones, `--replace` — overwrite, `--dry-run` — show prompts. Output — `img/<name>.jpg` and `img/images.json` with statuses; each image's log is in `--work/<name>/`.
4. While images are generating, build the site (step 5), referencing the future `img/<name>.jpg`.
5. After the notification, open each JPG via Read and check: no text or letters, consistent style, the scene reads clearly, no deformities. For a defect — **one** regeneration with a corrected prompt (`--only … --replace`). Replace an image that still fails with a diagram or an accent block — there must be no broken links.

If Codex is unavailable, build the site without images, with diagrams only; say so in your reply.

## 5. Site

```
Concept/<slug>/
  index.html     — comparison home page
  offer-1.html   — landing page for offer 1
  offer-2.html   — landing page for offer 2
  offer-3.html   — landing page for offer 3
  style.css      — shared styles
  img/           — Codex illustrations + images.json
```

- Home and landing structure — `design.md` §2; every landing page must have **«Коротко о сути»** right below the hero, **at least 2 SVG diagrams** and **3 illustrations** (hero + a 2-frame storyboard with captions).
- Diagrams — inline SVG per the rules in `design.md` §3 (colors via `var(--…)`, `role="img"`, `aria-label`, legible at 360px). Check the geometry.
- Style — `design.md` §5: minimalism, dark theme, responsive, plain HTML + CSS, relative links.
- Navigation: on landing pages — «← Все предложения» and the neighboring offers; on the home page, cards link to the landing pages and show a hero thumbnail.
- Home page footer: date, who took part (Claude, Codex, images — Codex image_gen), sources.

Check before replying:
- all pairs passed §3a; the difference table matches the actual texts, diagrams and scenes;
- all files are in place; every `href`/`src` points to an existing file (by script: collect `href="…"` and `src="…"` and check with `test -f`);
- no empty spots, "TODO", "Lorem";
- if a browser is available (Claude in Chrome or the built-in one) — it does not open `file://`: start `python -m http.server <port> --bind 127.0.0.1` in the site folder (in the background), check pages at 375px and ~1100px per `design.md` §3 (no horizontal scroll, diagram labels no smaller than 13px and not overlapping), then stop the server and close the tab; optional.
- If there are many pages or diagrams repeat, build the site with a Python script in the scratchpad (offer data + diagram functions) rather than by hand: it is more consistent and easier to edit.

## 6. Reply (in Russian, concise)

1. The topic in one line and who took part (Claude, Codex; how many images were generated, whether there were regenerations or gaps).
2. The offers with each one's decisive difference — one line each (under the §3a exception, state the actual number and the reason for the constraint): `N. Name — positioning in one sentence`.
3. Recommendation: which one is stronger and why, in one or two sentences; the main risk to test first.
4. Path to the site: `Concept/<slug>/index.html`.
5. Models: Claude researcher — <model, effort>; Codex — <model, effort / not run>; illustrations — Codex image_gen.
