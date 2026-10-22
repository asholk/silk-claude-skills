# silk-claude-skills

Набор скилов для [Claude Code](https://claude.com/claude-code) на русском языке. Скилы превращают короткую команду («доработай…», «предложи…», «концепт…») в повторяемый процесс: Claude ставит задачу субагентам, при желании подключает Codex как второе мнение, проверяет результат и кратко отчитывается.

Скил — это папка с файлом `SKILL.md` (YAML-шапка `name` + `description` и инструкции) и, при необходимости, скриптами. Claude подгружает скил сам, когда запрос подходит под описание, или по команде `/<имя-скила>`. Подробнее — в статье [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills).

## Скилы

| Скил | Команда / фраза | Что делает |
|---|---|---|
| [`dorabotay`](./dorabotay) | `/dorabotay`, «доработай …» | Быстрая правка: код пишет субагент, ревью — субагент Fable, главный процесс проверяет находки и при критических замечаниях отправляет на исправление |
| [`razrabotay`](./razrabotay) | `/razrabotay`, «разработай …» | Поиск лучших практик и алгоритмов → план (Fable) → реализация субагентом → ревью (Fable) и проверка → отчёт |
| [`staged-development`](./staged-development) | `/staged-development`, «поэтапно» | Крупная задача: план из этапов (Codex, запасной — Fable), параллельные субагенты волнами, мониторинг с ETA, коммит на задачу, общее ревью (Codex, запасной — Fable) и прогон тестов |
| [`predlozhi`](./predlozhi) | `/predlozhi`, «предложи …», «что улучшить» | Два независимых аналитика (Claude Fable + Codex) → одна таблица предложений с пользой и сложностью, без правок кода |
| [`concept`](./concept) | `/concept`, «концепт …» | Два исследователя → три разных предложения → мини-сайт: страница сравнения и три лендинга со схемами и иллюстрациями |
| [`optimum`](./optimum) | `/optimum`, «оптимум», «экономно» | Выбор модели и effort под тип задачи, правила делегирования субагентам, короткие промпты и ответы, дешёвые проверки качества — по официальным рекомендациям Anthropic; надстройка к оркестрирующим скилам |
| [`obsidian-style`](./obsidian-style) | срабатывает сам при работе с Obsidian | Применяет официальный стайлгайд Obsidian к UI-текстам, настройкам, командам и README плагинов |

## Установка

### Через маркетплейс плагинов (рекомендуется)

В Claude Code:

```
/plugin marketplace add asholk/silk-claude-skills
```

Затем установите нужные наборы:

```
/plugin install silk-dev@silk-claude-skills
/plugin install silk-concept@silk-claude-skills
/plugin install silk-obsidian@silk-claude-skills
```

| Набор | Скилы |
|---|---|
| `silk-dev` | `dorabotay`, `razrabotay`, `staged-development`, `predlozhi` |
| `silk-concept` | `concept` |
| `silk-obsidian` | `obsidian-style` |

### Вручную

Склонируйте репозиторий и скопируйте (или свяжите символической ссылкой) нужные папки в `~/.claude/skills/` — тогда скилы доступны во всех проектах:

```bash
git clone https://github.com/asholk/silk-claude-skills.git
cp -r silk-claude-skills/dorabotay ~/.claude/skills/
```

Для одного проекта — в `.claude/skills/` в корне проекта. После установки перезапустите Claude Code и спросите «какие скилы доступны?».

## Требования

- **Claude Code** с инструментом `Agent` (субагенты).
- **[Codex CLI](https://github.com/openai/codex)** — необязательно. `predlozhi`, `concept` и `staged-development` используют его как второго аналитика, планировщика или ревьюера; без Codex скилы работают только на Claude и сообщают об этом.
- **Python 3 + [Pillow](https://pypi.org/project/pillow/)** — для генерации иллюстраций в `concept` (`gen_images.py`).
- Ожидание чужих сборок в `dorabotay`, `razrabotay` и `staged-development` написано на PowerShell (Windows); на других ОС этот шаг нужно адаптировать.

## Устройство

```
<скил>/
  SKILL.md          # шапка (name, description, argument-hint) + инструкции
  *.md              # справочники, которые скил читает по ходу работы
  *.py              # вспомогательные скрипты
.claude-plugin/
  marketplace.json  # описание наборов для /plugin marketplace
```

## Как сделать свой скил

Начните с папки и `SKILL.md`:

```markdown
---
name: my-skill
description: Что делает скил и когда его использовать — Claude выбирает скил по этому описанию.
---

# My skill

Инструкции для Claude.
```

Подробнее — [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) и [спецификация Agent Skills](https://agentskills.io).

## Лицензия

[MIT](./LICENSE)
