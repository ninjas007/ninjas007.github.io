from __future__ import annotations

import re
from pathlib import Path


def title_from_name(name: str) -> str:
    base = name.strip().replace("_", " ").replace("-", " ")
    base = re.sub(r"\s+", " ", base).strip()
    return " ".join(w.capitalize() if w.islower() else w for w in base.split())


def read_text_any(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def guess_language(path: Path, text: str) -> str:
    ext = path.suffix.lower().lstrip(".")
    if ext in {"php", "js", "html"}:
        return ext
    if "<?php" in text or "$" in text:
        return "php"
    if "function " in text or "const " in text or "let " in text:
        return "js"
    return ""


def html_to_md(html: str) -> str:
    html = html.replace("\r\n", "\n")
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)

    def repl_img(m: re.Match) -> str:
        src = m.group(1).strip()
        alt = (m.group(2) or "").strip() or "image"
        return f"\n\n![{alt}]({src})\n\n"

    html = re.sub(
        r"<img[^>]*?src=\"([^\"]+)\"[^>]*?(?:alt=\"([^\"]*)\")?[^>]*?>",
        repl_img,
        html,
        flags=re.IGNORECASE,
    )

    html = re.sub(r"<h[1-6][^>]*>", "\n\n## ", html, flags=re.IGNORECASE)
    html = re.sub(r"</h[1-6]>", "\n\n", html, flags=re.IGNORECASE)

    html = re.sub(r"<p[^>]*>", "\n\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</p>", "\n\n", html, flags=re.IGNORECASE)

    html = re.sub(r"<div[^>]*class=\"fw-bold\"[^>]*>", "\n\n### ", html, flags=re.IGNORECASE)
    html = re.sub(r"</div>", "\n\n", html, flags=re.IGNORECASE)

    html = re.sub(r"<[^>]+>", "", html)
    html = re.sub(r"\n{3,}", "\n\n", html).strip()
    return html


def convert_file(path: Path) -> Path | None:
    if path.suffix.lower() == ".md":
        return None

    text = read_text_any(path).strip("\n")
    target = path.with_suffix(".md") if path.suffix else path.with_name(path.name + ".md")
    title = title_from_name(path.stem if path.suffix else path.name)

    if path.suffix.lower() == ".html":
        md_body = html_to_md(text)
        md = f"# {title}\n\n{md_body}\n"
    else:
        lang = guess_language(path, text)
        fence = f"```{lang}".rstrip()
        md = f"# {title}\n\n{fence}\n{text}\n```\n"

    target.write_text(md, encoding="utf-8")
    path.unlink()
    return target


def main() -> None:
    root = Path(__file__).resolve().parent
    articles = root / "articles"

    converted: list[Path] = []
    for path in sorted(p for p in articles.rglob("*") if p.is_file()):
        new_path = convert_file(path)
        if new_path:
            converted.append(new_path.relative_to(root))

    print(f"Converted {len(converted)} files:")
    for p in converted:
        print("-", p.as_posix())


if __name__ == "__main__":
    main()

