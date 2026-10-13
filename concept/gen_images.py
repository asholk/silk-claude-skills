# -*- coding: utf-8 -*-
"""concept/gen_images.py: генерация иллюстраций концепта через Codex CLI (встроенный image_gen).

Спецификация — JSON-файл:
{
  "style": "общий стилевой блок на английском (палитра, техника, настроение)",
  "avoid": "чего избегать (необязательно)",
  "images": [
    {"name": "offer-1-hero", "aspect": "16:9", "prompt": "сцена на английском"},
    {"name": "offer-1-scene", "aspect": "4:3", "prompt": "..."}
  ]
}

Каждая картинка — отдельный запуск `codex exec`, не больше --jobs параллельно (по умолчанию 2).
Результат: <out>/<name>.jpg и <out>/images.json (статус каждой картинки).

  python -I gen_images.py spec.json --out D:/site/img
  python -I gen_images.py spec.json --out D:/site/img --only offer-1-hero --replace
  python -I gen_images.py spec.json --out D:/site/img --dry-run
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ASPECTS = {"16:9": 16 / 9, "3:2": 3 / 2, "4:3": 4 / 3, "1:1": 1.0, "3:4": 3 / 4}
WIDTH = {"16:9": 1600, "3:2": 1500, "4:3": 1400, "1:1": 1100, "3:4": 1000}

INSTRUCTION = """\
You are generating ONE illustration for a product-concept landing page.
Use the built-in image_gen tool exactly once to generate one image with aspect ratio {aspect} ({orient}).
Pass the full specification below to image_gen as the prompt (translate anything non-English into English, keep every visual requirement).
The image must contain no text, letters, numbers, captions, labels, UI text, logos, brand names, signatures or watermarks.
Do not write any files, do not run shell commands, do not copy or move the result.
After generation reply with only the absolute path of the generated PNG file (one line), nothing else.

=== SPECIFICATION ===
Style: {style}

Scene: {prompt}

Avoid: {avoid}
"""

DEFAULT_AVOID = ("any text or lettering, logos, watermarks, cluttered backgrounds, stock-photo look, "
                 "uncanny faces, extra fingers, neon, heavy gradients")


def log(msg: str) -> None:
    print(f"[concept-img {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def codex_cmd() -> list[str]:
    exe = shutil.which("codex")
    if not exe:
        raise RuntimeError("Codex CLI не найден в PATH")
    if exe.lower().endswith((".cmd", ".bat")) or os.name == "nt":
        # npm-шим ломает кавычки и кириллицу через cmd.exe — запускаем node напрямую
        base = Path(exe).parent
        js = base / "node_modules" / "@openai" / "codex" / "bin" / "codex.js"
        node = base / "node.exe"
        node_s = str(node) if node.is_file() else shutil.which("node")
        if js.is_file() and node_s:
            return [node_s, str(js)]
    return [exe]


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))


def kill_tree(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.kill()
    except OSError:
        pass


PNG_RE = re.compile(r"([A-Za-z]:[\\/][^\r\n\"'<>|*?`]*?\.png|/[^\r\n\"'<>|*?`]*?\.png)", re.I)


def find_png(jsonl: Path, last: Path, started: float) -> Path:
    thread_id, mentioned = None, []
    texts = [last.read_text(encoding="utf-8", errors="replace") if last.exists() else ""]
    for line in jsonl.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "thread.started":
            thread_id = ev.get("thread_id")
        texts.append(line)
    for t in texts:
        for m in PNG_RE.findall(t):
            p = Path(m.replace("\\\\", "\\"))
            if p.is_file() and p not in mentioned:
                mentioned.append(p)
    if thread_id:
        tdir = codex_home() / "generated_images" / thread_id
        pngs = sorted(tdir.glob("*.png"), key=lambda p: p.stat().st_mtime) if tdir.is_dir() else []
        if pngs:
            return next((p for p in mentioned if p in pngs), pngs[-1])
    for p in mentioned:
        if p.stat().st_mtime >= started - 5:
            return p
    raise RuntimeError(f"PNG не найден (thread_id={thread_id}); ответ Codex: {texts[0].strip()[:300] or 'пустой'}")


def to_jpg(png: Path, out: Path, aspect: str) -> tuple[int, int]:
    from PIL import Image
    target = ASPECTS[aspect]
    with Image.open(png) as im:
        im = im.convert("RGB")
        w, h = im.size
        r = w / h
        if abs(r - target) / target > 0.03:  # центрированный кроп до нужных пропорций
            if r > target:
                nw = round(h * target)
                im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            else:
                nh = round(w / target)
                im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        tw = min(WIDTH[aspect], im.size[0])
        im = im.resize((tw, round(tw / target)), Image.LANCZOS)
        tmp = out.with_suffix(".tmp.jpg")
        im.save(tmp, "JPEG", quality=86, optimize=True, progressive=True)
        os.replace(tmp, out)
        return im.size


def generate(item: dict, spec: dict, out_dir: Path, work: Path, timeout: int, model: str | None) -> dict:
    name, aspect = item["name"], item.get("aspect", "16:9")
    out = out_dir / f"{name}.jpg"
    job = work / name
    job.mkdir(parents=True, exist_ok=True)
    orient = "landscape" if ASPECTS[aspect] > 1 else "square" if ASPECTS[aspect] == 1 else "portrait"
    prompt = INSTRUCTION.format(aspect=aspect, orient=orient, style=spec.get("style", "").strip(),
                                prompt=item["prompt"].strip(), avoid=spec.get("avoid") or DEFAULT_AVOID)
    (job / "prompt.txt").write_text(prompt, encoding="utf-8")
    jsonl, last = job / "codex.jsonl", job / "last.md"
    cmd = codex_cmd() + ["exec", "--skip-git-repo-check", "--json", "-s", "workspace-write",
                         "-C", str(job), "-o", str(last)]
    if model:
        cmd += ["-m", model]
    t0 = time.time()
    log(f"{name}: старт ({aspect})")
    with open(jsonl, "wb") as so, open(job / "stderr.txt", "wb") as se:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=so, stderr=se, cwd=str(job))
        proc.stdin.write(prompt.encode("utf-8"))
        proc.stdin.close()
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            proc.wait()
            raise RuntimeError(f"не уложился в {timeout} c")
    png = find_png(jsonl, last, t0)
    size = to_jpg(png, out, aspect)
    sec = round(time.time() - t0)
    log(f"{name}: готово за {sec} c → {out}")
    return {"name": name, "status": "ok", "file": out.name, "size": f"{size[0]}x{size[1]}",
            "seconds": sec, "png": str(png)}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path, required=True, help="папка для JPG (например <сайт>/img)")
    ap.add_argument("--only", default="", help="имена через запятую")
    ap.add_argument("--replace", action="store_true", help="перезаписывать существующие JPG")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=900, help="секунд на одну картинку")
    ap.add_argument("--model", default=None)
    ap.add_argument("--work", type=Path, default=None, help="папка логов (по умолчанию во временной)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    items = spec.get("images") or []
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    if only:
        items = [i for i in items if i["name"] in only]
    for i in items:
        if i.get("aspect", "16:9") not in ASPECTS:
            print(f"Неизвестный aspect у {i['name']}: {i.get('aspect')} (допустимо: {', '.join(ASPECTS)})")
            return 2
    a.out.mkdir(parents=True, exist_ok=True)
    work = a.work or Path(tempfile.gettempdir()) / "concept-img" / time.strftime("%Y%m%d-%H%M%S")
    results = []
    todo = []
    for i in items:
        if (a.out / f"{i['name']}.jpg").exists() and not a.replace:
            results.append({"name": i["name"], "status": "skipped", "file": f"{i['name']}.jpg"})
        else:
            todo.append(i)
    if a.dry_run:
        for i in todo:
            print(f"--- {i['name']} ({i.get('aspect', '16:9')})\n{i['prompt']}\n")
        print(f"Будет сгенерировано: {len(todo)}, пропущено: {len(results)}; логи: {work}")
        return 0
    log(f"картинок: {len(todo)}, параллельно: {a.jobs}, логи: {work}")
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        futs = {ex.submit(generate, i, spec, a.out, work, a.timeout, a.model): i for i in todo}
        for f in cf.as_completed(futs):
            name = futs[f]["name"]
            try:
                results.append(f.result())
            except Exception as e:  # noqa: BLE001 — одна неудача не должна валить остальные
                log(f"{name}: ОШИБКА — {e}")
                results.append({"name": name, "status": "error", "error": str(e), "log": str(work / name)})
    order = {i["name"]: n for n, i in enumerate(spec.get("images") or [])}
    results.sort(key=lambda r: order.get(r["name"], 999))
    manifest = a.out / "images.json"
    old = {}
    if manifest.exists():
        try:
            old = {r["name"]: r for r in json.loads(manifest.read_text(encoding="utf-8"))}
        except (ValueError, KeyError, TypeError):
            old = {}
    old.update({r["name"]: r for r in results})
    manifest.write_text(json.dumps(sorted(old.values(), key=lambda r: order.get(r["name"], 999)),
                                   ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(r["status"] == "ok" for r in results)
    err = sum(r["status"] == "error" for r in results)
    log(f"итого: готово {ok}, ошибок {err}, пропущено {len(results) - ok - err}; {manifest}")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
