"""SEO helpers: canonical URLs, meta tags, SERP overrides, FAQ JSON-LD."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from app.config import DOMAIN
from app.utils import CONTENT_DIR, load_school_data


def build_canonical_url(path: str, lang: str | None = None) -> str:
    canonical = f"{DOMAIN}{path}"
    if lang == "kr":
        return f"{canonical}?lang=kr"
    return canonical


def build_hreflang_urls(path: str) -> dict[str, str]:
    return {
        "en": build_canonical_url(path),
        "ko": build_canonical_url(path, "kr"),
        "x-default": build_canonical_url(path),
    }


def default_updated_at() -> str:
    _, updated_at = load_school_data("en")
    return updated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d")


def site_stats(lang: str = "en") -> dict[str, int | str]:
    schools, updated_at = load_school_data(lang)
    return {
        "total_schools": len(schools),
        "updated_at": updated_at or default_updated_at(),
    }


def content_lastmod(*filenames: str) -> str:
    timestamps: list[float] = []
    for filename in filenames:
        filepath = os.path.join(CONTENT_DIR, filename)
        if os.path.exists(filepath):
            timestamps.append(os.path.getmtime(filepath))
    if not timestamps:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d")


def build_meta_title(raw_title: str, lang: str = "en", suffix: str = "JP Campus") -> str:
    year = datetime.now(timezone.utc).strftime("%Y")
    base = f"[{year}] {raw_title}"
    title = f"{base} | {suffix}"
    return title[:68]


def build_meta_description(raw_description: str, fallback: str) -> str:
    text = (raw_description or "").strip() or fallback
    if len(text) <= 155:
        return text
    return f"{text[:152].rstrip()}..."


# GSC에서 CTR이 이미 강한 가이드는 메타/구조화 데이터를 건드리지 않음.
_HIGH_CTR_GUIDE_SLUGS = frozenset({"coe-denial", "university-clubs"})

# 저CTR·고노출 위주 SERP 메타만 덮어씀 (slug, "en"|"kr").
_GUIDE_SERP_OVERRIDES: dict[tuple[str, str], dict[str, str]] = {
    ("amazon-prime-student", "en"): {
        "title": "Amazon Prime Student Japan: Price, Benefits & Eligibility (2026)",
        "description": (
            "Prime Student Japan pricing vs regular Prime, shipping benefits, Prime Video, "
            "student eligibility, and whether it saves money for international students."
        ),
    },
    ("amazon-prime-student", "kr"): {
        "title": "일본 아마존 프라임 스튜던트: 가격·혜택·가입 조건 (2026)",
        "description": (
            "일반 프라임 대비 학생 요금, 배송·영상 혜택, 유학생 가입 시 확인할 조건을 "
            "짧게 비교합니다."
        ),
    },
    ("sim-card-guide", "kr"): {
        "title": "일본 유학생 SIM·휴대폰: 통신사·알뜰폰(MVNO) 비교와 개통 절차",
        "description": (
            "docomo/Softbank/KDDI와 MVNO 특징, 유학생에게 맞는 요금제 고르는 기준, "
            "개통 시 준비물을 정리했습니다."
        ),
    },
    ("eju-subjects", "en"): {
        "title": "EJU Subject Tests: Japan & World, Math, Science — How to Choose (2026)",
        "description": (
            "Pick EJU subjects with admissions in mind: syllabus scope, study order, and how "
            "Japan & the World, Science, and Math scores fit university requirements."
        ),
    },
}


def _guide_lang_key(lang: str) -> str:
    return "kr" if lang == "kr" else "en"


def apply_guide_serp_overrides(slug: str, lang: str, item: dict) -> tuple[str, str]:
    if slug in _HIGH_CTR_GUIDE_SLUGS:
        title = item.get("title", "Study in Japan Guide")
        desc = item.get("description", "")
        return title, desc
    lk = _guide_lang_key(lang)
    ov = _GUIDE_SERP_OVERRIDES.get((slug, lk))
    if not ov:
        return item.get("title", "Study in Japan Guide"), item.get("description", "")
    return ov.get("title", item.get("title", "")), ov.get("description", item.get("description", ""))


def guide_faq_json_ld(slug: str, lang: str) -> str | None:
    if slug in _HIGH_CTR_GUIDE_SLUGS:
        return None
    lk = _guide_lang_key(lang)
    key = (slug, lk)
    faq_map: dict[tuple[str, str], list[tuple[str, str]]] = {
        ("housing", "en"): [
            (
                "What are the main housing options for international students in Japan?",
                "Most students choose between school dormitories (ryo), share houses, or private apartments. "
                "Each differs in upfront costs, flexibility, and commute time.",
            ),
            (
                "Which housing type usually has the lowest move-in cost?",
                "School dormitories often have lower upfront costs than private apartments, but availability and rules vary by school.",
            ),
            (
                "What should I check before signing a rental contract in Japan?",
                "Review key money (reikin), deposit (shikikin), renewal fees, fire insurance, and cancellation terms with your school or agent.",
            ),
        ],
        ("housing", "kr"): [
            (
                "일본 유학생 주거는 어떤 선택지가 있나요?",
                "기숙사(寮), 쉐어하우스, 자취(원룸·아파트)가 대표적이며 초기비용·통학·규칙이 서로 다릅니다.",
            ),
            (
                "초기비용을 줄이려면 어떤 유형이 유리할까요?",
                "학교 기숙사는 원룸 대비 초기비용 부담이 적은 경우가 많지만, 공실과 규칙을 먼저 확인해야 합니다.",
            ),
            (
                "계약 전 꼭 확인해야 할 항목은 무엇인가요?",
                "礼金·敷金·更新料·火災保険·解約条件 등을 서면으로 확인하고, 학교 안내 또는 공인 중개와 절차를 맞추는 것이 안전합니다.",
            ),
        ],
        ("amazon-prime-student", "en"): [
            (
                "How much does Amazon Prime Student cost in Japan?",
                "Pricing is lower than regular Prime; compare monthly and annual student plans against how often you ship and stream.",
            ),
            (
                "Who can sign up for Amazon Prime Student in Japan?",
                "Eligibility depends on Amazon’s student verification rules; confirm your student status and account region requirements before subscribing.",
            ),
        ],
        ("amazon-prime-student", "kr"): [
            (
                "일본에서 아마존 프라임 스튜던트는 얼마인가요?",
                "일반 프라임보다 낮은 월/연 요금이 특징이며, 배송·스트리밍 이용 빈도에 따라 이득이 달라집니다.",
            ),
            (
                "유학생도 가입할 수 있나요?",
                "아마존의 학생 인증·계정 지역 조건을 충족해야 하므로, 가입 전 요건을 확인하는 것이 좋습니다.",
            ),
        ],
        ("sim-card-guide", "kr"): [
            (
                "유학생은 일본에서 어떤 통신 선택지가 있나요?",
                "대형 통신사(MNO)와 저가 알뜰폰(MVNO) 중에서 데이터·통화 필요량과 체류 기간에 맞게 고를 수 있습니다.",
            ),
            (
                "개통할 때 무엇을 준비해야 하나요?",
                "여권·재류카드 등 신분과 주소 확인 서류가 필요한 경우가 많습니다. 절차는 회사·매장마다 다릅니다.",
            ),
        ],
        ("eju-subjects", "en"): [
            (
                "Which EJU subject tests should I take?",
                "Choose subjects based on each university program’s requirements, then align your study plan to the official syllabus scope.",
            ),
            (
                "Is Japan and the World required for every university?",
                "Requirements vary by school and faculty; always verify the latest admissions bulletin for your target programs.",
            ),
        ],
    }
    rows = faq_map.get(key)
    if not rows:
        return None
    entities = []
    for q, a in rows:
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    payload = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return json.dumps(payload, ensure_ascii=False)
