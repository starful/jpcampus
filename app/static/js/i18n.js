// app/static/js/i18n.js

const translations = {
    ko: {
        // ... 기존 코드 유지 ...
        opt_region_all: "📍 지역 (전체)", opt_shinjuku: "신주쿠 (교통 편리)", opt_takadanobaba: "다카다노바바 (학생가)", 
        opt_shinokubo: "신오쿠보 (코리아타운)", opt_ikebukuro: "이케부쿠로 (생활 편리)", opt_shibuya: "시부야/하라주쿠",
        opt_nippori: "닛포리 (저렴한 물가)", opt_chiba: "치바현 (전체)",
        opt_price_all: "💰 학비 (1년 기준)", opt_price_80: "80만엔 ↓ (초가성비)", opt_price_85: "85만엔 ↓ (저렴)", opt_price_90: "90만엔 ↓ (평균)",
        opt_nation_all: "🌏 국적 비율", opt_global: "🇺🇸 서구권/다국적 (회화↑)", opt_kr_low: "🇰🇷 한국인 적은 곳", 
        opt_cn_high: "🇨🇳 한자권 (진학 분위기)", opt_vn_high: "🇻🇳 동남아 학생 활발",
        opt_scale_all: "👥 학교 규모", opt_scale_large: "대규모 (500명↑)", opt_scale_medium: "중규모 (200~500명)", opt_scale_small: "가족적 (200명↓)",
        opt_career_all: "🎓 진학/목표", opt_career_grad: "대학원 진학 위주", opt_career_univ: "대학 진학 위주", opt_career_voc: "전문학교/취업 위주",
        opt_special_all: "🎯 특화/목적", opt_special_art: "🎨 미술/디자인", opt_special_biz: "💼 비즈니스/취업",
        opt_special_short: "✈️ 단기/워킹홀리데이", opt_special_jlpt: "📚 JLPT 고득점 반",
        opt_dorm_all: "🛏️ 기숙사", opt_dorm_yes: "기숙사 있음 (전체)", opt_dorm_single: "👤 1인실 보유",
        opt_scholarship_all: "🏅 장학금 제도", opt_scholarship_yes: "장학금 있음",
        opt_eju_all: "📝 EJU 대책", opt_eju_yes: "EJU 수업 있음", opt_eju_science: "⚗️ 이과/수학 대응",
        opt_convo_all: "🗣️ 수업 스타일", opt_convo_yes: "회화/커뮤니케이션 중심",
        opt_env_all: "🏙️ 주변 환경", opt_env_quiet: "조용한 주택가/외곽", opt_env_active: "활기찬 도심/번화가",

        // [신규] 초기화 버튼 추가
        btn_search: "이 조건으로 검색하기", btn_reset: "필터 초기화", 

        txt_result: "검색 결과:", txt_schools: "개교", inf_fee: "1년 학비", inf_ppl: "명",
        btn_back: "← 지도 메인으로 돌아가기", lbl_capacity: "총 정원", lbl_total: "재적 학생수", lbl_korea: "한국인 비율", lbl_fee: "학비 (1년 추정)",
        ttl_features: "🏫 학교 특징", txt_no_data: "정보 없음", ttl_course: "📚 코스 및 학비", ttl_career: "📊 진학 실적 (최근)", 
        lbl_grad: "대학원", lbl_univ: "대학", lbl_voc: "전문학교", ttl_loc: "🗺️ 위치", btn_official: "공식 상세 정보 확인하기",
        legend_art: "미술/디자인", legend_cheap: "가성비 (82만엔↓)", legend_academic: "진학/EJU", legend_normal: "일반/기타"
    },
    ja: {
        opt_region_all: "📍 地域 (全て)", opt_shinjuku: "新宿 (交通便利)",
        opt_price_all: "💰 学費 (1年分)", opt_price_80: "80万円 ↓ (格安)", opt_price_85: "85万円 ↓", opt_price_90: "90万円 ↓",
        opt_nation_all: "🌏 国籍比率", opt_global: "🇺🇸 多国籍 (会話重視)", opt_kr_low: "🇰🇷 韓国人少なめ",
        opt_scale_all: "👥 規模", opt_scale_large: "大規模 (500名↑)",
        opt_career_all: "🎓 進路/目標", opt_career_grad: "大学院重視",
        opt_special_all: "🎯 特化/目的", opt_special_art: "🎨 美大/美術", opt_special_biz: "💼 ビジネス",
        opt_special_short: "✈️ 短期/ワーホリ", opt_special_jlpt: "📚 JLPT対策",
        opt_dorm_all: "🛏️ 寮", opt_dorm_yes: "提携あり", opt_dorm_single: "👤 個室あり",
        opt_scholarship_all: "🏅 奨学金", opt_scholarship_yes: "制度あり",
        opt_eju_all: "📝 EJU対策", opt_eju_yes: "授業あり", opt_eju_science: "⚗️ 理系/数学",
        opt_convo_all: "🗣️ 授業スタイル", opt_convo_yes: "会話中心",
        opt_env_all: "🏙️ 環境", opt_env_quiet: "静かな住宅街", opt_env_active: "賑やかな都心",

        // [신규]
        btn_search: "検索する", btn_reset: "リセット",

        txt_result: "結果:", txt_schools: "校", inf_fee: "年間学費", inf_ppl: "名",
        btn_back: "← マップに戻る", lbl_capacity: "定員", lbl_total: "在籍学生数", lbl_korea: "韓国人比率", lbl_fee: "学費 (1年推定)",
        ttl_features: "🏫 特徴", txt_no_data: "データなし", ttl_course: "📚 コース", ttl_career: "📊 実績", 
        lbl_grad: "大学院", lbl_univ: "大学", lbl_voc: "専門", ttl_loc: "🗺️ アクセス", btn_official: "公式情報",
        legend_art: "美術/デザイン", legend_cheap: "格安 (82万円↓)", legend_academic: "進学/EJU", legend_normal: "一般"
    },
    en: {
        opt_region_all: "📍 Region (All)", opt_shinjuku: "Shinjuku",
        opt_price_all: "💰 Tuition (1yr)", opt_price_80: "¥800k ↓", opt_price_85: "¥850k ↓", opt_price_90: "¥900k ↓",
        opt_nation_all: "🌏 Nationality", opt_global: "🇺🇸 Global", opt_kr_low: "🇰🇷 Low Korean Ratio",
        opt_scale_all: "👥 Size", opt_scale_large: "Large",
        opt_career_all: "🎓 Career", opt_career_grad: "Grad School",
        opt_special_all: "🎯 Specialized", opt_special_art: "🎨 Art", opt_special_biz: "💼 Business",
        opt_special_short: "✈️ Short-term/Holiday", opt_special_jlpt: "📚 JLPT Prep",
        opt_dorm_all: "🛏️ Dorm", opt_dorm_yes: "Available", opt_dorm_single: "👤 Single Room",
        opt_scholarship_all: "🏅 Scholarship", opt_scholarship_yes: "Yes",
        opt_eju_all: "📝 EJU Prep", opt_eju_yes: "Yes", opt_eju_science: "⚗️ Science/Math",
        opt_convo_all: "🗣️ Style", opt_convo_yes: "Conversation",
        opt_env_all: "🏙️ Env", opt_env_quiet: "Quiet", opt_env_active: "Active",

        // [신규]
        btn_search: "Search", btn_reset: "Reset",

        txt_result: "Results:", txt_schools: " schools", inf_fee: "Annual Fee", inf_ppl: "students",
        btn_back: "← Back", lbl_capacity: "Capacity", lbl_total: "Total", lbl_korea: "Korean Ratio", lbl_fee: "Est. Fee",
        ttl_features: "🏫 Features", txt_no_data: "No data", ttl_course: "📚 Courses", ttl_career: "📊 Career", 
        lbl_grad: "Grad", lbl_univ: "Univ", lbl_voc: "Vocational", ttl_loc: "🗺️ Location", btn_official: "Details",
        legend_art: "Art/Design", legend_cheap: "Cheap (<¥820k)", legend_academic: "Academic/EJU", legend_normal: "General"
    }
};

let currentLang = localStorage.getItem('lang') || 'ko';

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });

    if (typeof applyFilters === "function") {
        applyFilters();
    }
}