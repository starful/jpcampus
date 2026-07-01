"""Load school/guide Markdown from app/content with lang fallback."""
from __future__ import annotations

import os
from typing import Literal

import frontmatter
import markdown

from app.utils import CONTENT_DIR

ContentKind = Literal["school", "guide"]
MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "nl2br"]


class ContentNotFoundError(FileNotFoundError):
    """Raised when no markdown file exists for the requested content."""


def resolve_md_path(identifier: str, lang: str, kind: ContentKind) -> str:
    if kind == "school":
        filename = f"{identifier}_kr.md" if lang == "kr" else f"{identifier}.md"
    else:
        filename = f"guide_{identifier}_kr.md" if lang == "kr" else f"guide_{identifier}.md"

    md_path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(md_path) and lang == "kr":
        if kind == "school":
            md_path = os.path.join(CONTENT_DIR, f"{identifier}.md")
        else:
            md_path = os.path.join(CONTENT_DIR, f"guide_{identifier}.md")

    if not os.path.exists(md_path):
        raise ContentNotFoundError(identifier)
    return md_path


def load_post(md_path: str) -> tuple[frontmatter.Post, str]:
    post = frontmatter.load(md_path)
    content_html = markdown.markdown(post.content, extensions=MARKDOWN_EXTENSIONS)
    return post, content_html


def load_school_content(school_id: str, lang: str) -> tuple[dict, str, str]:
    """Return (item metadata, item_type, content_html)."""
    md_path = resolve_md_path(school_id, lang, "school")
    post, content_html = load_post(md_path)
    item = dict(post.metadata)
    item_type = "university" if item.get("category") == "university" else "school"
    return item, item_type, content_html


def load_guide_content(slug: str, lang: str) -> tuple[dict, str]:
    """Return (item metadata, content_html)."""
    md_path = resolve_md_path(slug, lang, "guide")
    post, content_html = load_post(md_path)
    item = dict(post.metadata)
    item.setdefault("id", slug)
    return item, content_html
