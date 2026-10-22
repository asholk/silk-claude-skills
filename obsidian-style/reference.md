# Obsidian style guide digest (fallback if the site is unavailable)

## Language
- Think, reason, plan and write internal notes, briefs and subagent/Codex prompts in English.
- Reply to the user in Russian: chat messages, questions, progress updates, reports and tables. Files the user will read (reports, sites, docs, commit messages) also stay in Russian unless the project's own conventions say otherwise.
- When delegating, tell subagents and Codex to think in English; their results come back to you, and you present them to the user in Russian.

Source: https://obsidian.md/ru/help/style-guide (captured 2026-10-01). The current version is on the site.

## Terminology

- «Сочетание клавиш» (keyboard shortcut), not hotkey — except for the name of the feature itself.
- «Выбрать» (select), not «нажать/кликнуть»; tap — only for touch actions on mobile.
- «Заметка» — a Markdown file; «файл» — other extensions.
- «Название заметки», not «заголовок заметки»; «активная заметка», not «текущая».
- «Папка», not «директория»; «тип файла», not «формат файла» (unless it's about a data format).
- heading, not header; sidebar as one word; sync, not synchronise; search term, not search query.
- maximum/minimum in full, not max/min; perform (a command), not invoke/execute.
- Products start with Obsidian: Obsidian Sync, Obsidian Publish.

## Wording

- Simple words, active voice, explicit phrasing, no idioms.
- English — American spelling (organize).

## Case

- Sentence case: «Как Obsidian хранит данные», not «Как Obsidian Хранит Данные».
- UI elements — exactly as in the app.

## Interface

- Button text — in **bold**.
- UI navigation path — with → : **Настройки → Плагины сообщества**.
- «Нижний левый угол» (adjective), «внизу слева» (noun); don't give a direction for settings.
- Vertically — «над» / «под».
- «Открыть» a note (the target is hidden), «переключиться» (both are open).

## Keys

- A single key with a symbol: «клавиша дефис (-)».
- Combinations without spaces: `Ctrl+Z` (Windows), `Command+Z` (macOS); not `Ctrl + Z`, not `Ctrl/Cmd+Z`.
- Same on all platforms — no OS: `Escape`.

## Markdown

- Blank lines between blocks.
- An em dash after a bold term: **Меню видов** — создание и переключение видов.
- Realistic examples (`task:(call OR schedule)`), not foo/bar.
- Imperative mood in headings and steps: «Настройте», not «Настройка».
- Lists — for independent items, requirements, parameters, steps; prose — for explanations and connected processes.
- Tables — only for comparisons, not for simple lists.
- Platforms: subsections «### Компьютер» and «### Мобильные устройства» only when there are significant differences.

## Callouts

| Type | Syntax | Default |
|-----|-----------|--------------|
| Подсказка | `> [!tip]-` | Collapsed |
| Информация | `> [!info]+` | Expanded |
| Предупреждение (потеря данных) | `> [!warning]+` | Never collapsed |
| Пример | `> [!example]-` | Collapsed |

## Links

- Wiki links `[[Название заметки#Раздел|описательный текст]]`, once per term per page, only if the target page gives meaningful context.

## Images and icons

- .png or .svg, 1920 x 1080 pixels, 65–75 % compression, only when it is hard to explain in words.
- Anchors: `#icon`, `#interface`, `#outline`.
- Icons: Lucide (`lucide-`) or Obsidian (`obsidian-icon-`), SVG 18x18, stroke 1.5, in `Attachments/icons`, embedded as `![[lucide-cog.svg#icon]]`.

## Metadata and translations

- The `description` property — up to 150 characters, an objective summary of the page.
- Translate everything: note names, folders, aliases, attachments, link text; check for broken links.
