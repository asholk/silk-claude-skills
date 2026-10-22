# Concept design: reference

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

Best practices for presenting ideas: Amazon PR/FAQ, the concept board "insight → benefit → reason to believe", Moore's positioning statement, JTBD job stories, NN/g storyboards, landing page structure 2024–2026, consistent AI illustrations. The numbers here are heuristics, not laws.

The site's visible text is in the language of the request (normally Russian); the Russian labels and headings quoted below are what the site shows.

## 1. Skeleton of each offer (hidden fields)

Fill in the **same** fields for each of the three offers: the landing page and an honest comparison on the home page are built from them.

| Field | Formula |
|---|---|
| **Positioning** | "For [who], who has [pain], [name] is a [category] that [key benefit]. Unlike [alternative], [main difference]". It is a clarity tool, not a slogan. |
| **Headline** | up to 10 words, an outcome for the user, not a feature name |
| **Subheadline** | 1–2 sentences: who, what they get, how |
| **Job story** | "When [situation], I want [motivation], so that [outcome]" |
| **Insight** | the customer's conflict in their own words (one or two sentences) |
| **Benefit** | 3 benefits as outcomes (no more: a long concept dilutes the message) |
| **Reason to believe** | mechanism, data, analogues, expert — why it will work |
| **Why now** | what makes the idea possible or needed right now |
| **Alternatives** | how the problem is solved today (2–3 options) |
| **Main risk** and **what to test first** | hypothesis + success metric |
| **Model** | price, format, monetization |

Also fill in the difference passport per `SKILL.md` §3a. The identical field skeleton is for comparison; the content must show different mechanics, scenarios and trade-offs.

5-second test: a person unfamiliar with the idea can answer "what is it, who is it for, what do I do next" from the first screen. If not, rewrite the headline.

## 2. Landing page structure

1. **Hero** — headline, subheadline, hero illustration, **one** CTA.
2. **«Коротко о сути» (TL;DR)** — a strip of three cards «Проблема · Решение · Почему сейчас», one sentence each, + positioning in one line below it.
3. **Insight** — the job story in large type + 2–3 pains; a "before / after" diagram.
4. **Benefit** — 3 benefits, each "pain → how we remove it" (value map).
5. **How it works** — a 3-step diagram with arrows (SVG).
6. **Scenario** — a storyboard of 2–3 AI frames with captions (a named character, a concrete situation) or a "day with the product" timeline.
7. **Why it will work (RTB)** — mechanism, analogues, data; an ecosystem diagram if there are several participants.
8. **Comparison with alternatives** — a 2×2 matrix or a "us / today / analogue" table.
9. **Risks and questions** — 5–8 objections in the user's voice in `<details>` + an honest "main risk / what to test first" block.
10. **Final CTA** — repeat the promise + a link to the neighboring offer.

Section headings are conclusions («Утро без крика за три недели» — "A morning without shouting in three weeks"), not labels («Возможности» — "Features"). One idea per section. Evidence sits next to the claim. A concept has no testimonials: a possible user quote is marked «сценарий».

The structure above defines meaning blocks. The "before / after" and "3 steps" diagrams are examples: choose forms that fit the real scenario, keeping at least two diagrams per landing page. Do not copy a scenario with names swapped.

### Home page (index.html)

Hero with the user's idea in one sentence → «Коротко» (3–5 lines: what we looked for, what we arrived at, what we recommend) → 3 cards (thumbnail, name, positioning, key benefit, main risk) → a comparison table on the same fields + 1–5 score bars on 4–5 criteria (benefit, ease of launch, difference from analogues, risk, cost) → a 2×2 matrix of the three offers → recommendation → best practices → footer with sources.

On the home page add the difference table and an explanation of each pair per `SKILL.md` §3a. The 1–5 scores do not replace it. If fewer options passed, apply the §3a exception to the whole site structure.

## 3. Diagrams (inline SVG)

Types — choose 2–3 per landing page; do not repeat the same set on all three:

- **3 steps**: icon circle + verb + result, arrows between steps; vertical on phones (two SVG versions, or flex with rotated arrows).
- **Before / after**: two columns with identical rows (time, steps, emotion); "before" in gray, "after" in the accent.
- **Day / journey timeline**: a horizontal line with 4–6 points; the points where the product is involved are in the accent.
- **Ecosystem**: product in the center, 3–6 nodes around it, labeled verb arrows, no crossings.
- **2×2 matrix**: axes — the main difference from positioning; our option in the accent, alternatives in gray.
- **Storyboard**: 3 AI frames in a row with numbers and captions (stacked on phones).

Legibility rules:

- No more than 7 elements, simple shapes (circles, rounded rectangles), labels directly on the diagram, no legends.
- Colors only via CSS variables (`fill="var(--accent)"`, `var(--muted)`, `var(--line)`, `var(--text)`) so the diagram works in the dark theme.
- `viewBox` + `width:100%`; SVG text at least 14px at 360px width — if it does not fit, move the labels into HTML below the diagram.
- Wide and narrow versions: classes `only-wide` / `only-narrow` and CSS with the same specificity as the general rule, otherwise `.diagram svg { display:block }` shows both: `.diagram svg.only-wide { display:none }`, `.diagram svg.only-narrow { display:block }` and the reverse in `@media (min-width:720px)`. A diagram with callouts on the right (a watch, a device) — in the narrow version, put the labels as a list below the drawing.
- Check: in a 375px-wide iframe, visible `svg text` has height ≥ 13px and label boxes do not overlap (getBoundingClientRect).
- `role="img"` and an `aria-label` with the gist of the diagram.
- Check the geometry: clock-face angles, sector proportions, labels matching their elements.

## 4. AI illustrations (Codex, `gen_images.py`)

Set: for each landing page a **hero (16:9)** + **2 scenario frames (4:3)**; no images are generated for the home page — cards use the landing heroes. 9 images total, named `offer-N-hero`, `offer-N-scene-1`, `offer-N-scene-2`.

**Style block** — one for the whole concept, in English, 40–80 words:
- technique: flat editorial illustration / soft vector / gouache — one per series;
- palette: 3–5 named colors matching the site's CSS tokens (background, text, three accents);
- light, texture, mood in one word; plenty of empty space, a light solid background;
- characters described once (age, hairstyle, clothing) and repeated verbatim in every scene.

**Scene** — one paragraph of 40–90 words in English: who, where, what they do, the product's key object in close-up, camera angle. One idea, one focus, room for text at the side for the hero. The plot comes from the job story and the storyboard — the image explains the section's meaning, it does not decorate.

The shared style unites the series, not the plots: each offer has its own action, key object and composition showing its distinctive mechanic. A change of color or clothing does not confirm a difference. Check finished images together with their captions per `SKILL.md` §3a. If an image does not convey the mechanic, fix it within the regeneration limit or replace it with an explanatory diagram.

For close-ups of a child's hands, explicitly write "small child-sized hands, short slender fingers" — otherwise the model draws adult hands.

**Don't:** text, letters, numbers on clock faces and screens, logos, brands of real devices (instead of «Яндекс Станция» — "a small smart speaker"), photorealism, stock "happy people with a laptop", extra objects. Labels, numbers and interface are added in HTML/SVG on top or alongside.

In HTML: `<img src="img/offer-1-hero.jpg" alt="…meaning of the frame…" loading="lazy" width height>`; do not set `loading` on the hero. If an image failed to generate, put a diagram or an accent-background block in its place, not a broken link.

## 5. Site visual style

- Minimalism: one font (system stack), a neutral palette + its own accent for each offer, plenty of whitespace, no decorative shadows, gradients or animations.
- Colors — variables in `:root`, dark theme via `prefers-color-scheme`.
- Content width up to ~1080px, 16px side gutters on phones, no horizontal scroll (wide tables in a wrapper with `overflow-x:auto`).
- Plain HTML + CSS with no build step; opens with a double click; all links relative.
