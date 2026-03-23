from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
from pathlib import Path


MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def read_text_any(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def publish_str(date: dt.date) -> str:
    return f"{date.day} {MONTHS[date.month - 1]} {date.year}"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\.[a-z0-9]+$", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "post"


def title_from_filename(path: Path) -> str:
    name = path.stem
    name = name.replace("_", " ").replace("-", " ").strip()
    return " ".join(w.capitalize() if w.islower() else w for w in name.split())


def extract_html_title(path: Path) -> str | None:
    try:
        text = read_text_any(path)
    except OSError:
        return None
    match = re.search(r"<title>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return title or None


def extract_md_title(path: Path) -> str | None:
    try:
        lines = read_text_any(path).splitlines()
    except OSError:
        return None
    for line in lines[:40]:
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip() or None
    return None


def guess_tags(text: str) -> list[str]:
    haystack = text.lower()
    tags: list[str] = []
    rules = [
        ("laravel", "Laravel"),
        ("git", "Git"),
        ("github", "GitHub"),
        ("docker", "Docker"),
        ("postgres", "PostgreSQL"),
        ("mysql", "MySQL"),
        ("sqlserver", "SQL Server"),
        ("sql-server", "SQL Server"),
        ("mqtt", "MQTT"),
        ("node", "Node.js"),
        ("nvm", "Node.js"),
        ("php", "PHP"),
        ("javascript", "JavaScript"),
        ("jquery", "jQuery"),
        ("linux", "Linux"),
        ("windows", "Windows"),
        ("xampp", "XAMPP"),
        ("woocommerce", "WordPress"),
        ("wordpress", "WordPress"),
        ("dompdf", "PDF"),
        ("wkhtmltopdf", "PDF"),
        ("laragon", "Laragon"),
        ("sweetalert", "SweetAlert"),
    ]
    for needle, tag in rules:
        if needle in haystack and tag not in tags:
            tags.append(tag)
    return tags[:4]


def main() -> None:
    root = Path(__file__).resolve().parent
    articles_dir = root / "articles"
    out_file = root / "data" / "articles.json"

    today = dt.date.today()
    items: list[dict] = []

    def add_item(
        *,
        title: str,
        url: str,
        type_: str,
        published_at: dt.date,
        tags: list[str],
        source_path: str | None = None,
    ) -> None:
        slug = slugify(title)
        items.append(
            {
                "id": len(items),
                "type": type_,
                "slug": slug,
                "title": title,
                "author": "Tilis Tiadi",
                "published_at": published_at.isoformat(),
                "publish": publish_str(published_at),
                "url": url,
                "reference_url": "",
                "article_url": url,
                "article_short_desc": "",
                "tags": tags,
                "source_path": source_path or "",
            }
        )

    # Videos (manual)
    add_item(
        title="Laravel 7: upload file attachment email",
        url="https://youtu.be/t8S2jB0sW4U",
        type_="video",
        published_at=today,
        tags=["Laravel", "Video"],
    )
    add_item(
        title="Customize SweetAlert HTML",
        url="https://youtu.be/y42yhG95wRY",
        type_="video",
        published_at=today,
        tags=["SweetAlert", "Video"],
    )

    if articles_dir.exists():
        for path in sorted(p for p in articles_dir.rglob("*.md") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            published_at = dt.date.fromtimestamp(path.stat().st_mtime)

            title = None
            title = extract_md_title(path)

            if not title:
                title = title_from_filename(path)

            tags = guess_tags(f"{rel} {title}")

            viewer_url = f"article.html?p={urllib.parse.quote(rel)}"
            add_item(
                title=title,
                url=viewer_url,
                type_="article",
                published_at=published_at,
                tags=tags,
                source_path=rel,
            )

    items.sort(key=lambda x: (x.get("published_at") or "", x.get("title") or ""), reverse=True)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(items, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} items -> {out_file}")


if __name__ == "__main__":
    main()
