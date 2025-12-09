/* app/static/js/i18n.js */

const translations = {
    en: {
        // --- [Filters] ---
        opt_region_all: "📍 Region (All)",
        opt_price_all: "💰 Tuition (1yr)", opt_price_70: "700k~ JPY", opt_price_75: "Under 750k", opt_price_80: "Under 800k", opt_price_85: "Under 850k",
        opt_nation_all: "🌏 Nationality", opt_global: "🇺🇸 Global/Western", opt_korea_low: "🇰🇷 Low Korean Ratio", opt_china_high: "🇨🇳 High Chinese", opt_vietnam_high: "🇻🇳 High Vietnamese",
        opt_scale_all: "👥 Size", opt_scale_large: "Large (500+)", opt_scale_medium: "Medium", opt_scale_small: "Small",
        opt_career_all: "🎓 Career Focus", opt_career_grad: "Grad School", opt_career_university: "University", opt_career_vocational: "Vocational/Job",
        opt_special_all: "🎯 Specialized", opt_special_art: "🎨 Art/Design", opt_special_biz: "💼 Business", opt_special_short: "✈️ Short-term", opt_special_jlpt: "📚 JLPT Prep",
        opt_dorm_all: "🛏️ Dormitory", opt_dorm_yes: "Available", opt_dorm_single: "Single Room", opt_dorm_school_owned: "School Owned",
        opt_scholarship_all: "🏅 Scholarship", opt_scholarship_yes: "Available",
        opt_eju_all: "📝 EJU Prep", opt_eju_yes: "Available", opt_eju_science: "⚗️ Science/Math", opt_eju_art: "🎨 Art Practical",
        opt_convo_all: "🗣️ Style", opt_convo_yes: "Conversation", opt_convo_activity: "Activities",
        opt_env_all: "🏙️ Environment", opt_env_active: "City Center", opt_env_quiet: "Quiet Area",

        // --- [Main & Map] ---
        page_title: "Japan Language School Map Search & Compare",
        filter_univ_ph: "🏫 Search University (e.g. Waseda)",
        filter_univ_desc: "* Enter a university name to see its <strong>location</strong> and schools with strong <strong>admission records</strong>.",
        search_btn: "Search",
        reset_btn: "Reset",

        // Map InfoWindow
        iw_univ_home: "Official Website",
        iw_school_detail: "View Details",
        iw_capacity: "Capacity",
        iw_min_fee: "Min Fee",
        unit_person: "",
        unit_money: "0k JPY",

        // Detail Page
        btn_back: "← Back to Map",
        lbl_capacity: "Capacity",
        ttl_features: "Features",
        ttl_loc: "Location",

        // --- [Guides Section (Main Page)] ---
        guide_main_title: "📚 Essential Guides for Japan",
        guide_cost_title: "💰 1-Year Cost Breakdown",
        guide_cost_desc: "Tuition, housing, and living expenses. A realistic budget analysis for studying in Tokyo.",
        guide_school_title: "🏫 5 Criteria for Choosing a School",
        guide_school_desc: "How to choose the right school for university advancement, employment, or conversation.",
        guide_visa_title: "✈️ Visa Application Guide",
        guide_visa_desc: "Step-by-step guide from document preparation to COE issuance and visa application.",
        guide_housing_title: "🏠 Dorm vs Share House vs Apartment",
        guide_housing_desc: "Pros and cons of each housing type and comparison of initial costs.",
        guide_view_all: "View All Guides >",

        // --- [Guide List Page] ---
        guide_list_title: "📚 Essential Guides for Studying in Japan",
        guide_list_desc: "Information you must know before studying in Japan, from preparation to living tips.",
        
        // Guide Card Titles
        guide_cost_t: "💰 1-Year Cost Breakdown",
        guide_school_t: "🏫 5 Criteria for Choosing a School",
        guide_visa_t: "✈️ Visa Application Guide",
        guide_housing_t: "🏠 Dorm vs Share House vs Apartment",
        guide_parttime_t: "🍔 Part-time Jobs & Wages",
        guide_exam_t: "📚 EJU vs JLPT Guide",
        guide_prep_t: "🧳 Pre-departure Checklist",
        guide_settle_t: "📱 Resident Registration & Bank",
        guide_ins_t: "🏥 Health Insurance & Hospital",
        guide_region_t: "🌏 Tokyo vs Osaka vs Rural",

        // Guide Card Descriptors
        guide_cost_d: "Tuition, housing, and living expenses. A realistic budget analysis.",
        guide_school_d: "How to choose the right school for university, job, or conversation.",
        guide_visa_d: "Step-by-step guide from COE issuance to visa application.",
        guide_housing_d: "Pros/cons of each housing type and initial cost comparison.",
        guide_parttime_d: "Work permit, recommended jobs by level, and average wages.",
        guide_exam_d: "Differences between EJU and JLPT for university admission.",
        guide_prep_d: "Must-bring items like Hanko, adapter, and documents.",
        guide_settle_d: "Guide to City Hall procedures, SIM card, and bank account.",
        guide_ins_d: "How to apply for insurance fee reduction and use hospitals.",
        guide_region_d: "Comparison of standard language, living costs, and atmosphere.",

        // Tags
        tag_cost: "Cost/Budget", tag_school: "Selection", tag_visa: "Visa", tag_house: "Housing",
        tag_work: "Part-time", tag_exam: "Exam", tag_prep: "Packing", tag_settle: "Settlement",
        tag_ins: "Insurance", tag_region: "Region",

        // Footer & Common
        btn_back_main: "Back to Main Map"
    },
    ko: {
        // --- [Filters] ---
        opt_region_all: "📍 지역 (전체)", 
        opt_price_all: "💰 학비 (1년 기준)", opt_price_70: "70만엔대 (초저렴)", opt_price_75: "75만엔 ↓", opt_price_80: "80만엔 ↓", opt_price_85: "85만엔 ↓",
        opt_nation_all: "🌏 국적 비율", opt_global: "🇺🇸 다국적 (서양권 10%↑)", opt_korea_low: "🇰🇷 한국인 소수 (30%↓)", opt_china_high: "🇨🇳 한자권 중심", opt_vietnam_high: "🇻🇳 동남아 중심",
        opt_scale_all: "👥 학교 규모", opt_scale_large: "대규모 (500명↑)", opt_scale_medium: "중규모", opt_scale_small: "소수정예",
        opt_career_all: "🎓 진학 실적", opt_career_grad: "대학원 진학 우수", opt_career_university: "명문대 진학 우수", opt_career_vocational: "취업/전문학교 위주",
        opt_special_all: "🎯 특화 코스", opt_special_art: "🎨 미대 입시", opt_special_biz: "💼 비즈니스/취업", opt_special_short: "✈️ 단기/워킹홀리데이", opt_special_jlpt: "📚 JLPT 대비",
        opt_dorm_all: "🛏️ 기숙사", opt_dorm_yes: "기숙사 있음", opt_dorm_single: "1인실 보유", opt_dorm_school_owned: "학교 소유",
        opt_scholarship_all: "🏅 장학금", opt_scholarship_yes: "교내 장학금 있음",
        opt_eju_all: "📝 EJU 대책", opt_eju_yes: "EJU 수업 있음", opt_eju_science: "⚗️ 이과 있음", opt_eju_art: "🎨 실기 지도",
        opt_convo_all: "🗣️ 수업 분위기", opt_convo_yes: "회화 중심", opt_convo_activity: "문화 체험 많음",
        opt_env_all: "🏙️ 주변 환경", opt_env_active: "번화가", opt_env_quiet: "조용한 동네",

        // --- [Main & Map] ---
        page_title: "일본 전국 일본어학교 지도 검색 & 비교 서비스, JP Campus",
        filter_univ_ph: "🏫 대학 이름 검색 (예: 와세다)",
        filter_univ_desc: "* 대학명을 입력하면 <strong>대학 위치</strong>와 <strong>진학 실적</strong>이 우수한 학교를 지도에 표시합니다.",
        search_btn: "검색하기",
        reset_btn: "초기화",
        
        // Map InfoWindow
        iw_univ_home: "대학 홈페이지",
        iw_school_detail: "상세 정보 보기",
        iw_capacity: "정원",
        iw_min_fee: "최저",
        unit_person: "명",
        unit_money: "만엔",

        // Detail Page
        btn_back: "← 지도 메인으로",
        lbl_capacity: "총 정원",
        ttl_features: "학교 특징",
        ttl_loc: "위치",

        // --- [Guides Section (Main Page)] ---
        guide_main_title: "📚 일본 유학 핵심 가이드",
        guide_cost_title: "💰 1년 비용 총정리",
        guide_cost_desc: "학비, 기숙사비, 생활비까지. 도쿄 유학에 실제로 필요한 초기 자금과 예산을 분석합니다.",
        guide_school_title: "🏫 학교 선택 기준 5가지",
        guide_school_desc: "진학, 취업, 회화 등 내 목적에 딱 맞는 일본어학교를 고르는 방법을 알려드립니다.",
        guide_visa_title: "✈️ 비자 신청 완벽 가이드",
        guide_visa_desc: "복잡한 서류 준비부터 COE 발급, 대사관 사증 신청까지 단계별로 정리했습니다.",
        guide_housing_title: "🏠 기숙사 vs 원룸",
        guide_housing_desc: "기숙사, 쉐어하우스, 자취 중 어디가 좋을까요? 장단점과 초기 비용을 비교해드립니다.",
        guide_view_all: "가이드 전체 보기 >",

        // --- [Guide List Page] ---
        guide_list_title: "📚 일본 유학 필수 가이드",
        guide_list_desc: "일본 어학연수 준비부터 생활 꿀팁까지, 예비 유학생이 꼭 알아야 할 정보를 정리했습니다.",

        // Guide Card Titles
        guide_cost_t: "💰 1년 비용 총정리",
        guide_school_t: "🏫 학교 선택 기준 5가지",
        guide_visa_t: "✈️ 비자 신청 완벽 가이드",
        guide_housing_t: "🏠 기숙사 vs 원룸 비교",
        guide_parttime_t: "🍔 아르바이트 구하기 & 시급",
        guide_exam_t: "📚 EJU와 JLPT의 차이점",
        guide_prep_t: "🧳 출국 전 필수 체크리스트",
        guide_settle_t: "📱 주소등록, 폰, 통장 개설",
        guide_ins_t: "🏥 국민건강보험료와 병원",
        guide_region_t: "🌏 도쿄 vs 오사카 vs 지방",

        // Guide Card Descriptors
        guide_cost_d: "학비, 기숙사비, 생활비까지. 도쿄 유학에 실제로 필요한 초기 자금과 예산을 분석합니다.",
        guide_school_d: "진학, 취업, 회화 등 내 목적에 딱 맞는 일본어학교를 고르는 방법을 알려드립니다.",
        guide_visa_d: "복잡한 서류 준비부터 COE 발급, 대사관 사증 신청까지 단계별로 정리했습니다.",
        guide_housing_d: "기숙사, 쉐어하우스, 자취 중 어디가 좋을까요? 장단점과 초기 비용을 비교해드립니다.",
        guide_parttime_d: "자격외활동허가서 받는 법부터 일본어 실력별 추천 알바, 평균 시급 정보까지.",
        guide_exam_d: "일본 대학 진학을 위한 EJU와 취업을 위한 JLPT의 차이점과 준비 전략.",
        guide_prep_d: "도장, 돼지코, 상비약 등 한국에서 꼭 챙겨가야 할 물건과 가져가면 안 되는 것들.",
        guide_settle_d: "재류카드 주소 등록부터 유심 개통, 유초은행 통장 개설까지 초기 정착 가이드.",
        guide_ins_d: "유학생도 보험료를 내야 할까? 감면 신청 방법과 아플 때 병원 이용하는 팁.",
        guide_region_d: "지역별 물가, 분위기, 표준어 사용 여부 등 나에게 맞는 유학 지역 찾기.",

        // Tags
        tag_cost: "비용/예산", tag_school: "학교선택", tag_visa: "비자/서류", tag_house: "숙소/생활",
        tag_work: "생활/알바", tag_exam: "시험/진학", tag_prep: "출국준비", tag_settle: "현지정착",
        tag_ins: "의료/보험", tag_region: "지역정보",

        // Footer & Common
        btn_back_main: "메인 지도로 돌아가기"
    }
};

// [중요] 기본값을 항상 'en'으로 강제하고, localStorage가 있으면 그걸 따름
let currentLang = 'en'; 
if (localStorage.getItem('lang')) {
    currentLang = localStorage.getItem('lang');
}

function setLanguage(lang) {
    if (!translations[lang]) return;
    
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    // HTML 텍스트 변경
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });

    // 검색창 Placeholder
    const univInput = document.getElementById("filter-univ");
    if (univInput && translations[lang]['filter_univ_ph']) {
        univInput.placeholder = translations[lang]['filter_univ_ph'];
    }

    // 지도 갱신 (데이터가 있을 때만)
    if (typeof SCHOOLS_DATA !== "undefined" && SCHOOLS_DATA.length > 0) {
        if (typeof applyFilters === "function") {
            applyFilters(); 
        } else if (typeof renderMarkers === "function") {
            renderMarkers(SCHOOLS_DATA);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setLanguage(currentLang);
});