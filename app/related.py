"""Related content pickers for detail and compare pages."""
from __future__ import annotations

from app.utils import assign_thumbnails, load_guides, load_school_data


def pick_related_guides(item: dict, item_type: str, lang: str, limit: int = 4) -> list[dict]:
    guides = load_guides(lang)
    source_text = ""
    if item_type == "guide":
        source_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    else:
        basic = item.get("basic_info", {}) or {}
        source_text = f"{basic.get('name_en', '')} {basic.get('address', '')}".lower()

    city_keywords = ["tokyo", "osaka", "kyoto", "nagoya", "fukuoka", "hokkaido", "japan"]
    matched = [kw for kw in city_keywords if kw in source_text]
    related = []
    for guide in guides:
        guide_text = f"{guide.get('title', '')} {guide.get('description', '')}".lower()
        if any(kw in guide_text for kw in matched):
            related.append(guide)
    if len(related) < limit:
        existing_links = {g.get("link") for g in related}
        for guide in guides:
            if guide.get("link") not in existing_links:
                related.append(guide)
            if len(related) >= limit:
                break
    return related[:limit]


def pick_compare_guides(selected: list[dict], lang: str, limit: int = 4) -> list[dict]:
    if not selected:
        return []
    related: list[dict] = []
    seen: set[str] = set()
    for item in selected:
        item_type = "university" if item.get("category") == "university" else "school"
        for guide in pick_related_guides(item, item_type, lang, limit=2):
            link = guide.get("link")
            if link and link not in seen:
                seen.add(link)
                related.append(guide)
            if len(related) >= limit:
                return related[:limit]
    for guide in load_guides(lang):
        link = guide.get("link")
        if link and link not in seen:
            seen.add(link)
            related.append(guide)
        if len(related) >= limit:
            break
    return related[:limit]


def pick_related_schools(item: dict, lang: str, limit: int = 4) -> list[dict]:
    schools, _ = load_school_data(lang)
    source_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    wants_university = "university" in source_text or "eju" in source_text
    wants_school = "language school" in source_text or "jlpt" in source_text
    city_keywords = ["東京", "大阪", "京都", "名古屋", "福岡", "tokyo", "osaka", "kyoto", "nagoya", "fukuoka"]

    related = []
    for school in schools:
        basic = school.get("basic_info", {}) or {}
        address = basic.get("address", "")
        address_lower = address.lower()
        category = school.get("category")

        if wants_university and category != "university":
            continue
        if wants_school and category == "university":
            continue
        if any(kw in source_text for kw in ["tokyo", "東京"]) and not ("tokyo" in address_lower or "東京都" in address):
            continue
        if any(kw in source_text for kw in ["osaka", "大阪"]) and not ("osaka" in address_lower or "大阪府" in address):
            continue

        if any(kw in source_text for kw in city_keywords):
            related.append(school)
        if len(related) >= limit:
            break

    if len(related) < limit:
        for school in schools:
            if school not in related:
                related.append(school)
            if len(related) >= limit:
                break

    return assign_thumbnails(related[:limit], "university" if wants_university else "school")
