"""HTML page routes, sitemap, robots, ads.txt."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response

from app.config import ADS_TXT_CONTENT, DOMAIN, FAMILY_SITE_ID, GOOGLE_MAPS_API_KEY, SHOW_STAYS_UI
from app.affiliate import affiliate_context
from app.content_loader import ContentNotFoundError, load_guide_content, load_school_content, load_stay_content
from app.content_badges import enrich_items
from app.deps import templates
from app.family_sites import cross_links_for, inject_family_context
from app.related import (
    pick_compare_guides,
    pick_nearby_schools,
    pick_nearby_stays,
    pick_related_guides,
    pick_related_schools,
)
from app.seo import (
    apply_guide_serp_overrides,
    build_canonical_url,
    build_hreflang_urls,
    build_meta_description,
    build_meta_title,
    content_lastmod,
    default_updated_at,
    guide_faq_json_ld,
    stay_faq_json_ld,
)
from app.social_share import share_context
from app.utils import (
    assign_thumbnails,
    build_compare_export,
    calculate_tag_counts,
    compare_fee_value,
    get_entity_filters,
    get_region_filters,
    get_stay_type_filters,
    get_type_filters,
    get_university_type_filters,
    get_ui_text,
    load_guides,
    load_school_data,
    load_stay_data,
    prepare_compare_items,
    resolve_guide_thumbnail,
)

router = APIRouter()


def page_context(
    path: str,
    lang: str,
    *,
    title: str,
    description: str,
) -> dict:
    return {
        "canonical_url": build_canonical_url(path, lang),
        "current_lang": lang,
        "hreflang_urls": build_hreflang_urls(path),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title(title, lang),
        "meta_description": build_meta_description(description, description),
    }


def _campus_address(item: dict) -> str | None:
    basic = item.get("basic_info") or {}
    return basic.get("address") or item.get("address")


def _detail_cross_links(lang: str, item: dict | None = None, categories: list | None = None):
    address = _campus_address(item) if item else None
    return cross_links_for(
        FAMILY_SITE_ID,
        lang,
        address=address,
        categories=categories,
    )


@router.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    entries: list[dict[str, str]] = []

    def add_entry(path: str, lastmod: str, changefreq: str, priority: str):
        alternates = build_hreflang_urls(path)
        entries.append({
            "loc": alternates["en"],
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority,
            "alt_en": alternates["en"],
            "alt_ko": alternates["ko"],
            "alt_default": alternates["x-default"],
        })
        entries.append({
            "loc": alternates["ko"],
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority,
            "alt_en": alternates["en"],
            "alt_ko": alternates["ko"],
            "alt_default": alternates["x-default"],
        })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    add_entry("/", today, "daily", "1.0")
    static_pages = ["/about", "/guide", "/schools", "/universities", "/contact", "/policy", "/compare"]
    if SHOW_STAYS_UI:
        static_pages.append("/stays")
    for page in static_pages:
        add_entry(page, today, "weekly", "0.8")

    schools_en, _ = load_school_data("en")
    for school in schools_en:
        school_id = school.get("id")
        if not school_id:
            continue
        add_entry(
            f"/school/{school_id}",
            content_lastmod(f"{school_id}.md", f"{school_id}_kr.md"),
            "weekly",
            "0.8",
        )

    guides_en = load_guides("en")
    for guide in guides_en:
        slug = guide["link"].split("/")[-1].split("?")[0]
        add_entry(
            f"/guide/{slug}",
            content_lastmod(f"guide_{slug}.md", f"guide_{slug}_kr.md"),
            "weekly",
            "0.7",
        )

    stays_en, _ = load_stay_data("en")
    for stay in stays_en:
        stay_id = stay.get("id")
        if not stay_id:
            continue
        add_entry(
            f"/stay/{stay_id}",
            content_lastmod(f"stay_{stay_id}.md", f"stay_{stay_id}_kr.md"),
            "weekly",
            "0.75",
        )

    unique_entries = {(e["loc"], e["lastmod"], e["changefreq"], e["priority"]): e for e in entries}
    xml_items = []
    for entry in sorted(unique_entries.values(), key=lambda x: x["loc"]):
        xml_items.append(
            f"""
        <url>
            <loc>{xml_escape(entry["loc"])}</loc>
            <lastmod>{entry["lastmod"]}</lastmod>
            <changefreq>{entry["changefreq"]}</changefreq>
            <priority>{entry["priority"]}</priority>
            <xhtml:link rel="alternate" hreflang="en" href="{xml_escape(entry["alt_en"])}" />
            <xhtml:link rel="alternate" hreflang="ko" href="{xml_escape(entry["alt_ko"])}" />
            <xhtml:link rel="alternate" hreflang="x-default" href="{xml_escape(entry["alt_default"])}" />
        </url>"""
        )

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:xhtml="http://www.w3.org/1999/xhtml">
        {''.join(xml_items)}
    </urlset>"""
    return Response(content=xml_content, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, lang: str = Query("en")):
    schools_data, updated_at = load_school_data(lang)
    stays_data, stays_updated = load_stay_data(lang) if SHOW_STAYS_UI else ([], None)
    all_guides = load_guides(lang)
    ui = get_ui_text(lang)

    featured_candidates = [g for g in all_guides if g.get('is_featured')]
    if not featured_candidates:
        featured_candidates = all_guides[:6]
    else:
        featured_candidates = featured_candidates[:6]
    featured_guides = enrich_items(featured_candidates)
    featured_links = {g["link"] for g in featured_guides}

    latest_schools = enrich_items(assign_thumbnails([s for s in schools_data if s.get('category') != 'university'][:6], "school"))
    latest_universities = enrich_items(assign_thumbnails([s for s in schools_data if s.get('category') == 'university'][:6], "university"))
    latest_stays = enrich_items(stays_data[:6]) if SHOW_STAYS_UI else []
    tags_with_counts = calculate_tag_counts(schools_data)

    university_list = []
    for s in schools_data:
        if s.get('category') == 'university':
            b_info = s.get('basic_info') or {}
            university_list.append({
                "name_ja": b_info.get('name_ja', ''),
                "name_en": b_info.get('name_display') or b_info.get('name_en') or ''
            })

    return templates.TemplateResponse(request, "index.html", {
        "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "stays_json": json.dumps({"stays": stays_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "updated_at": updated_at,
        "stays_updated": stays_updated,
        "total_schools": len(schools_data),
        "total_stays": len(stays_data),
        "show_stays_ui": SHOW_STAYS_UI,
        "featured_guides": featured_guides,
        "latest_schools": latest_schools,
        "latest_universities": latest_universities,
        "latest_stays": latest_stays,
        "latest_guides": enrich_items([g for g in all_guides if g["link"] not in featured_links][:6]),
        "tags_with_counts": tags_with_counts,
        "university_list_json": university_list,
        "current_lang": lang,
        "ui": ui,
        "type_filters": get_type_filters(lang),
        "university_type_filters": get_university_type_filters(lang),
        "entity_filters": get_entity_filters(lang),
        "stay_type_filters": get_stay_type_filters(lang) if SHOW_STAYS_UI else [],
        "region_filters": get_region_filters(lang),
        "canonical_url": build_canonical_url("/", lang),
        "hreflang_urls": build_hreflang_urls("/"),
        "meta_title": build_meta_title(
            "JP Campus (Official) — Japan Language Schools, Universities & Map"
            if lang != "kr"
            else "JP Campus 공식 — 일본 어학원·대학 비교 지도와 유학 가이드",
            lang,
        ),
        "meta_description": build_meta_description(
            (
                "Official JP Campus: compare Japanese language schools and universities on an interactive map, "
                "plus practical visa, housing, admissions, and student-life guides."
            )
            if lang != "kr"
            else (
                "JP Campus 공식 사이트: 일본 어학원·대학을 지도에서 비교하고, 비자·주거·입학·생활 "
                "실전 가이드를 한곳에서 확인하세요."
            ),
            (
                "Official JP Campus: compare Japanese language schools and universities on an interactive map, "
                "plus practical visa, housing, admissions, and student-life guides."
            ),
        ),
    })


@router.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str, lang: str = Query("en")):
    try:
        item, item_type, content_html = load_school_content(school_id, lang)
    except ContentNotFoundError:
        raise HTTPException(status_code=404, detail="School content file not found")

    share_title = (
        item.get("title")
        or item.get("basic_info", {}).get("name_en")
        or item.get("basic_info", {}).get("name_ja")
        or "School Guide"
    )
    ctx = share_context(DOMAIN, "school", school_id, share_title, lang)

    return templates.TemplateResponse(request, "detail.html", {
        "item": item, "item_type": item_type,
        "content_body": content_html, "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url(f"/school/{school_id}", lang),
        "hreflang_urls": build_hreflang_urls(f"/school/{school_id}"),
        "updated_at": default_updated_at(),
        "related_guides": pick_related_guides(item, item_type, lang),
        "nearby_stays": pick_nearby_stays(item, lang) if SHOW_STAYS_UI and item_type != "guide" else [],
        "show_stays_ui": SHOW_STAYS_UI,
        "meta_title": build_meta_title(share_title, lang),
        "meta_description": build_meta_description(
            item.get("description", ""),
            "Compare school details, tuition clues, and student-ready preparation tips."
        ),
        "faq_json_ld": None,
        "cross_site_links": _detail_cross_links(lang, item),
        **inject_family_context(FAMILY_SITE_ID, lang),
        **ctx,
    })


@router.get("/stay/{stay_id}", response_class=HTMLResponse)
async def read_stay_detail(request: Request, stay_id: str, lang: str = Query("en")):
    try:
        item, item_type, content_html = load_stay_content(stay_id, lang)
    except ContentNotFoundError:
        raise HTTPException(status_code=404, detail="Stay content file not found")

    basic = item.get("basic_info") or {}
    share_title = item.get("title") or basic.get("name_en") or "Student Housing"
    ctx = share_context(DOMAIN, "stay", stay_id, share_title, lang)

    stay_type = item.get("stay_type", "guesthouse")
    ui = get_ui_text(lang)
    stay_type_label = ui.get(f"stay_type_{stay_type}", stay_type)
    meta_raw_title = item.get("seo_title") or share_title
    meta_raw_desc = item.get("seo_description") or item.get("description", "")

    return templates.TemplateResponse(request, "detail.html", {
        "item": item,
        "item_type": item_type,
        "stay_type_label": stay_type_label,
        "content_body": content_html,
        "current_lang": lang,
        "ui": ui,
        "show_stays_ui": SHOW_STAYS_UI,
        "nearby_stays": [],
        "related_schools": pick_nearby_schools(item, lang),
        "canonical_url": build_canonical_url(f"/stay/{stay_id}", lang),
        "hreflang_urls": build_hreflang_urls(f"/stay/{stay_id}"),
        "updated_at": default_updated_at(),
        "related_guides": pick_related_guides(item, "stay", lang),
        "meta_title": build_meta_title(meta_raw_title, lang),
        "meta_description": build_meta_description(
            meta_raw_desc,
            "Foreigner-friendly student housing near Japanese language schools and universities.",
        ),
        "faq_json_ld": stay_faq_json_ld(item),
        "cross_site_links": _detail_cross_links(lang, item),
        **inject_family_context(FAMILY_SITE_ID, lang),
        **ctx,
    })


@router.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str, lang: str = Query("en")):
    try:
        item, content_html = load_guide_content(slug, lang)
    except ContentNotFoundError:
        raise HTTPException(status_code=404, detail="Guide content file not found")

    item["thumbnail"] = resolve_guide_thumbnail(item, slug)

    title_raw, desc_raw = apply_guide_serp_overrides(slug, lang, item)

    share_title = title_raw or item.get("title", "Study in Japan Guide")
    ctx = share_context(DOMAIN, "guide", slug, share_title, lang)

    return templates.TemplateResponse(request, "detail.html", {
        "item": item, "item_type": "guide",
        "content_body": content_html, "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url(f"/guide/{slug}", lang),
        "hreflang_urls": build_hreflang_urls(f"/guide/{slug}"),
        "updated_at": default_updated_at(),
        "related_schools": pick_related_schools(item, lang),
        "related_guides": pick_related_guides(item, "guide", lang),
        "nearby_stays": [],
        "show_stays_ui": SHOW_STAYS_UI,
        "meta_title": build_meta_title(title_raw or item.get("title", "Study in Japan Guide"), lang),
        "meta_description": build_meta_description(
            desc_raw,
            "Actionable study-in-Japan guide with practical decisions and student checklists."
        ),
        "faq_json_ld": guide_faq_json_ld(slug, lang),
        "cross_site_links": _detail_cross_links(lang, item),
        **inject_family_context(FAMILY_SITE_ID, lang),
        **affiliate_context(slug, lang=lang),
        **ctx,
    })


@router.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    schools = enrich_items(assign_thumbnails([s for s in schools_data if s.get('category') != 'university'], "school"))

    return templates.TemplateResponse(request, "list.html", {
        "items": schools, "item_type": "school",
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "description": "Browse all language schools across Japan." if lang == "en" else "일본 전역의 일본어학교를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/schools", lang),
        "hreflang_urls": build_hreflang_urls("/schools"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title(
            "Japanese Language Schools in Japan — Compare by City | JP Campus"
            if lang != "kr"
            else "일본 전국 일본어학교 목록 — 지역별 비교 | JP Campus",
            lang,
        ),
        "meta_description": build_meta_description(
            (
                "Browse Japanese language schools across Japan: compare areas, typical costs, and student-life notes, "
                "then open each school page for details."
            )
            if lang != "kr"
            else (
                "일본 전역 일본어학교를 지역·학비 등으로 살펴보고, 각 학교 상세 페이지로 이어지는 "
                "목록형 디렉터리입니다."
            ),
            "Compare language schools by city, tuition, and student lifestyle fit.",
        ),
    })


@router.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    universities = enrich_items(assign_thumbnails([s for s in schools_data if s.get('category') == 'university'], "university"))

    return templates.TemplateResponse(request, "list.html", {
        "items": universities, "item_type": "university",
        "title": "All Universities" if lang == 'en' else "일본 대학 목록",
        "description": "Explore universities in Japan for international students." if lang == "en" else "유학생을 위한 일본 대학교 정보를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/universities", lang),
        "hreflang_urls": build_hreflang_urls("/universities"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Universities in Japan for International Students", lang),
        "meta_description": build_meta_description(
            "Find university options in Japan with practical comparisons and prep guidance.",
            "Find university options in Japan with practical comparisons and prep guidance."
        ),
    })


@router.get("/stays", response_class=HTMLResponse)
async def stay_list(request: Request, lang: str = Query("en")):
    if not SHOW_STAYS_UI:
        return RedirectResponse(
            url=f"/guide/tokyo-student-housing-operators?lang={lang}",
            status_code=302,
        )

    stays_data, _ = load_stay_data(lang)
    stays = enrich_items(stays_data)

    return templates.TemplateResponse(request, "list.html", {
        "items": stays,
        "item_type": "stay",
        "title": "Student Housing" if lang == "en" else "숙소 일람",
        "description": (
            "Browse guesthouses, share houses, and monthly mansions for students in Japan."
            if lang == "en"
            else "유학생을 위한 게스트하우스·셰어하우스·먼슬리맨션을 확인하세요."
        ),
        "current_lang": lang,
        "ui": get_ui_text(lang),
        "show_stays_ui": True,
        "canonical_url": build_canonical_url("/stays", lang),
        "hreflang_urls": build_hreflang_urls("/stays"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title(
            "Student Housing in Japan — Guesthouse, Share House & Monthly | JP Campus"
            if lang != "kr"
            else "일본 유학생 숙소 일람 — 게스트·셰어·먼슬리 | JP Campus",
            lang,
        ),
        "meta_description": build_meta_description(
            (
                "Browse student-friendly housing across Japan: guesthouses, share houses, "
                "and monthly mansions with links to operator booking pages."
            )
            if lang != "kr"
            else (
                "일본 유학생용 게스트하우스·셰어하우스·먼슬리맨션을 한곳에서 살펴보고 "
                "각 숙소 상세·예약 링크로 이어지는 목록입니다."
            ),
            "Browse student housing options across Japan.",
        ),
    })


@router.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request, lang: str = Query("en")):
    guides = load_guides(lang)

    return templates.TemplateResponse(request, "list.html", {
        "items": guides, "item_type": "guide",
        "title": "Essential Guides" if lang == 'en' else "유학 가이드",
        "description": "Read practical study-abroad guides for life in Japan." if lang == "en" else "일본 유학 생활 실전 가이드를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/guide", lang),
        "hreflang_urls": build_hreflang_urls("/guide"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Essential Japan Study Guides", lang),
        "meta_description": build_meta_description(
            "Read practical guides on costs, housing, visas, and student life in Japan.",
            "Read practical guides on costs, housing, visas, and student life in Japan."
        ),
    })


@router.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request, ids: str = "", lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    school_by_id = {s["id"]: s for s in schools_data if s.get("id")}
    id_list = [value.strip() for value in ids.split(",") if value.strip()][:3]

    selected = []
    for school_id in id_list:
        item = school_by_id.get(school_id)
        if not item:
            continue
        item_type = "university" if item.get("category") == "university" else "school"
        assign_thumbnails([item], item_type)
        selected.append(item)

    fee_values = [compare_fee_value(item) for item in selected]
    fee_values = [value for value in fee_values if value is not None]
    min_fee = min(fee_values) if fee_values else None

    ui = get_ui_text(lang)
    prepared = prepare_compare_items(selected, lang)
    return templates.TemplateResponse(request, "compare.html", {
        "selected": prepared,
        "min_fee": min_fee,
        "related_guides": pick_compare_guides(prepared, lang),
        "compare_export": build_compare_export(prepared, lang, "JP Campus"),
        "current_lang": lang,
        "ui": ui,
        "canonical_url": build_canonical_url("/compare", lang),
        "hreflang_urls": build_hreflang_urls("/compare"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title(ui["meta_compare_title"], lang),
        "meta_description": build_meta_description(
            ui["meta_compare_desc"],
            "Compare Japanese language schools and universities side by side on JP Campus.",
        ),
    })


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "about.html", page_context(
        "/about", lang,
        title="About JP Campus",
        description="Learn how JP Campus helps international students choose schools in Japan.",
    ))


@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "contact.html", page_context(
        "/contact", lang,
        title="Contact JP Campus",
        description="Contact JP Campus for corrections, feedback, or collaboration.",
    ))


@router.get("/policy", response_class=HTMLResponse)
async def policy(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "policy.html", page_context(
        "/policy", lang,
        title="Privacy Policy",
        description="Read how JP Campus handles privacy, cookies, and data usage.",
    ))
