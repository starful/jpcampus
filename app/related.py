"""Related content pickers for detail and compare pages."""
from __future__ import annotations

import math

from app.utils import assign_thumbnails, load_guides, load_school_data, load_stay_data


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


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def pick_nearby_stays(item: dict, lang: str, limit: int = 4, radius_km: float = 3.0) -> list[dict]:
    loc = item.get("location") or {}
    lat, lng = loc.get("lat"), loc.get("lng")
    if lat is None or lng is None:
        basic = item.get("basic_info") or {}
        address = (basic.get("address") or "").lower()
        if "tokyo" not in address and "東京都" not in address:
            return []
        lat, lng = 35.6762, 139.6503

    stays, _ = load_stay_data(lang)
    scored: list[tuple[float, dict]] = []
    for stay in stays:
        sloc = stay.get("location") or {}
        slat, slng = sloc.get("lat"), sloc.get("lng")
        if slat is None or slng is None:
            continue
        dist = _haversine_km(float(lat), float(lng), float(slat), float(slng))
        if dist <= radius_km:
            stay = dict(stay)
            stay["distance_km"] = round(dist, 1)
            scored.append((dist, stay))

    scored.sort(key=lambda x: x[0])
    return [s for _, s in scored[:limit]]


def pick_nearby_schools(item: dict, lang: str, limit: int = 4, radius_km: float = 5.0) -> list[dict]:
    """Schools closest to a stay (or other geo item) by haversine distance."""
    loc = item.get("location") or {}
    lat, lng = loc.get("lat"), loc.get("lng")
    if lat is None or lng is None:
        return []

    schools, _ = load_school_data(lang)
    scored: list[tuple[float, dict]] = []
    for school in schools:
        sloc = school.get("location") or {}
        slat, slng = sloc.get("lat"), sloc.get("lng")
        if slat is None or slng is None:
            continue
        dist = _haversine_km(float(lat), float(lng), float(slat), float(slng))
        if dist <= radius_km:
            row = dict(school)
            row["distance_km"] = round(dist, 1)
            scored.append((dist, row))

    scored.sort(key=lambda x: x[0])
    nearby = [s for _, s in scored[:limit]]
    if not nearby:
        # Fall back to nearest schools even outside the radius.
        scored = []
        for school in schools:
            sloc = school.get("location") or {}
            slat, slng = sloc.get("lat"), sloc.get("lng")
            if slat is None or slng is None:
                continue
            dist = _haversine_km(float(lat), float(lng), float(slat), float(slng))
            row = dict(school)
            row["distance_km"] = round(dist, 1)
            scored.append((dist, row))
        scored.sort(key=lambda x: x[0])
        nearby = [s for _, s in scored[:limit]]

    return assign_thumbnails(nearby, "school")
