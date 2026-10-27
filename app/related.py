"""Related content pickers for detail and compare pages."""
from __future__ import annotations

from app.utils import assign_thumbnails, haversine_km, load_guides, load_school_data, load_stay_data


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


def _sorted_by_distance(
    lat: float, lng: float, candidates: list[dict], radius_km: float | None = None
) -> list[tuple[float, dict]]:
    scored: list[tuple[float, dict]] = []
    for candidate in candidates:
        cloc = candidate.get("location") or {}
        clat, clng = cloc.get("lat"), cloc.get("lng")
        if clat is None or clng is None:
            continue
        dist = haversine_km(float(lat), float(lng), float(clat), float(clng))
        if radius_km is None or dist <= radius_km:
            row = dict(candidate)
            row["distance_km"] = round(dist, 1)
            scored.append((dist, row))
    scored.sort(key=lambda x: x[0])
    return scored


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
    scored = _sorted_by_distance(lat, lng, stays, radius_km)
    return [s for _, s in scored[:limit]]


def pick_nearby_schools(item: dict, lang: str, limit: int = 4, radius_km: float = 5.0) -> list[dict]:
    """Schools closest to a stay (or other geo item) by haversine distance."""
    loc = item.get("location") or {}
    lat, lng = loc.get("lat"), loc.get("lng")
    if lat is None or lng is None:
        return []

    schools, _ = load_school_data(lang)
    scored = _sorted_by_distance(lat, lng, schools, radius_km)
    nearby = [s for _, s in scored[:limit]]
    if not nearby:
        # Fall back to nearest schools even outside the radius.
        scored = _sorted_by_distance(lat, lng, schools, None)
        nearby = [s for _, s in scored[:limit]]

    return assign_thumbnails(nearby, "school")
