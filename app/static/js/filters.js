/* app/static/js/filters.js — entity + detail (school/univ/stay) + region */

(function () {
    let allSchoolData = [];
    let allStayData = [];
    let currentEntityFilter = "all";
    let currentTypeFilter = "all";
    let currentUnivTypeFilter = "all";
    let currentStayTypeFilter = "all";
    let currentRegionFilter = "all";
    let currentFilteredSchools = [];
    let currentFilteredStays = [];

    const SHORT_TERM_KEYWORDS = ["short-term", "short term", "short_term", "단기", "短期"];
    const SCHOLARSHIP_KEYWORDS = ["scholarship", "장학금", "奨学金"];
    const BUSINESS_KEYWORDS = ["business japanese", "business jp", "비즈니스", "ビジネス", "business"];
    const ENGLISH_INTL_KEYWORDS = [
        "english", "international", "english-taught", "english program",
        "영어", "국제", "英語", "国際",
    ];
    const MAJOR_CITIES = [
        "福岡", "神戸", "札幌", "横浜", "仙台",
        "Fukuoka", "Kobe", "Sapporo", "Yokohama", "Sendai",
        "후쿠오카", "고베", "삿포로", "요코하마", "센다이",
    ];

    function getFeatures(school) {
        const rawFeatures = school.features;
        return Array.isArray(rawFeatures)
            ? rawFeatures.join(" ").toLowerCase()
            : String(rawFeatures || "").toLowerCase();
    }

    function getAddress(item) {
        return item.basic_info?.address || "";
    }

    function isUniversity(school) {
        return school.category === "university";
    }

    function isLanguageSchool(school) {
        return !isUniversity(school);
    }

    function featuresIncludeAny(features, keywords) {
        return keywords.some((kw) => features.includes(kw.toLowerCase()));
    }

    function getYearlyTuition(school) {
        const raw = school.tuition?.yearly_tuition;
        if (typeof raw === "number" && Number.isFinite(raw)) return raw;
        if (typeof raw === "string") {
            const digits = raw.replace(/[^\d]/g, "");
            if (digits) return Number(digits);
        }
        return null;
    }

    function matchesSchoolType(school, typeKey) {
        if (isUniversity(school)) return false;
        if (typeKey === "all") return true;

        const features = getFeatures(school);
        const capacity = school.basic_info?.capacity;

        switch (typeKey) {
            case "short_term":
                return featuresIncludeAny(features, SHORT_TERM_KEYWORDS)
                    || (features.includes("short") && features.includes("course"));
            case "scholarship":
                return featuresIncludeAny(features, SCHOLARSHIP_KEYWORDS);
            case "business":
                return featuresIncludeAny(features, BUSINESS_KEYWORDS);
            case "size_small":
                return typeof capacity === "number" && capacity > 0 && capacity <= 150;
            default:
                return true;
        }
    }

    function matchesUnivType(school, typeKey) {
        if (!isUniversity(school)) return false;
        if (typeKey === "all") return true;

        if (typeKey === "english_intl") {
            return featuresIncludeAny(getFeatures(school), ENGLISH_INTL_KEYWORDS);
        }

        const tuition = getYearlyTuition(school);
        if (tuition == null) return false;

        switch (typeKey) {
            case "tuition_low":
                return tuition <= 800000;
            case "tuition_mid":
                return tuition > 800000 && tuition < 1200000;
            case "tuition_high":
                return tuition >= 1200000;
            default:
                return true;
        }
    }

    function matchesEntitySchoolSimple(school) {
        if (currentEntityFilter === "stays") return false;
        if (currentEntityFilter === "language_schools") {
            return isLanguageSchool(school) && matchesSchoolType(school, currentTypeFilter);
        }
        if (currentEntityFilter === "universities") {
            return isUniversity(school) && matchesUnivType(school, currentUnivTypeFilter);
        }
        // all — show every school/university (subtype row is hidden)
        return true;
    }

    function addressHasAny(address, needles) {
        return needles.some((n) => address.includes(n));
    }

    function isTokyoAddress(address) {
        return addressHasAny(address, ["東京都", "東京", "Tokyo", "tokyo", "도쿄", "동경"]);
    }

    function isOsakaAddress(address) {
        return addressHasAny(address, ["大阪府", "大阪", "Osaka", "osaka", "오사카"]);
    }

    function isNagoyaAddress(address) {
        return addressHasAny(address, ["名古屋", "愛知", "Nagoya", "nagoya", "Aichi", "aichi", "나고야", "아이치"]);
    }

    function isKyotoAddress(address) {
        if (isTokyoAddress(address)) return false;
        return addressHasAny(address, ["京都府", "京都", "Kyoto", "kyoto", "교토"]);
    }

    function matchesRegion(item, regionKey) {
        if (regionKey === "all") return true;
        const address = getAddress(item);

        switch (regionKey) {
            case "tokyo":
                return isTokyoAddress(address);
            case "osaka":
                return isOsakaAddress(address);
            case "nagoya":
                return isNagoyaAddress(address);
            case "kyoto":
                return isKyotoAddress(address) && !isTokyoAddress(address);
            case "major_city":
                return !isTokyoAddress(address)
                    && !isOsakaAddress(address)
                    && !isNagoyaAddress(address)
                    && !isKyotoAddress(address)
                    && MAJOR_CITIES.some((city) => address.includes(city));
            default:
                return true;
        }
    }

    function stayOperator(stay) {
        const id = String(stay.id || "").toLowerCase();
        if (id.startsWith("oakhouse") || id.includes("oakhouse")) return "oakhouse";
        if (id.startsWith("sakura") || id.includes("sakura")) return "sakura";
        return "";
    }

    function matchesStayType(stay, typeKey) {
        if (typeKey === "all") return true;
        if (typeKey === "oakhouse" || typeKey === "sakura") {
            return stayOperator(stay) === typeKey;
        }
        return stay.stay_type === typeKey;
    }

    function sortByPublishedDesc(items) {
        return items.slice().sort((a, b) => {
            const da = String(a.published || "").slice(0, 10);
            const db = String(b.published || "").slice(0, 10);
            if (da !== db) return db.localeCompare(da);
            return String(a.id || "").localeCompare(String(b.id || ""));
        });
    }

    function computeFilteredSchools() {
        return sortByPublishedDesc(allSchoolData.filter((school) => (
            matchesEntitySchoolSimple(school) && matchesRegion(school, currentRegionFilter)
        )));
    }

    function computeFilteredStays() {
        if (currentEntityFilter === "language_schools" || currentEntityFilter === "universities") {
            return [];
        }
        if (currentEntityFilter === "schools") return [];
        const typeKey = currentEntityFilter === "stays" ? currentStayTypeFilter : "all";
        return sortByPublishedDesc(allStayData.filter((stay) => (
            matchesStayType(stay, typeKey) && matchesRegion(stay, currentRegionFilter)
        )));
    }

    function countLanguageSchools(regionKey, typeKey) {
        return allSchoolData.filter((x) => (
            isLanguageSchool(x)
            && matchesSchoolType(x, typeKey)
            && matchesRegion(x, regionKey)
        )).length;
    }

    function countUniversities(regionKey, univTypeKey) {
        return allSchoolData.filter((x) => (
            isUniversity(x)
            && matchesUnivType(x, univTypeKey || "all")
            && matchesRegion(x, regionKey)
        )).length;
    }

    function countStays(regionKey, stayTypeKey) {
        return allStayData.filter((x) => (
            matchesStayType(x, stayTypeKey) && matchesRegion(x, regionKey)
        )).length;
    }

    function countEntity(key) {
        const region = currentRegionFilter;
        if (key === "all") {
            return countLanguageSchools(region, "all")
                + countUniversities(region, "all")
                + countStays(region, "all");
        }
        if (key === "language_schools") {
            return countLanguageSchools(region, currentTypeFilter);
        }
        if (key === "universities") {
            return countUniversities(region, currentUnivTypeFilter);
        }
        if (key === "stays") {
            return countStays(region, currentStayTypeFilter);
        }
        if (key === "schools") {
            return countLanguageSchools(region, "all") + countUniversities(region, "all");
        }
        return 0;
    }

    function countForAxis(axis, key) {
        if (axis === "entity") return countEntity(key);
        if (axis === "stay_type") {
            return countStays(currentRegionFilter, key);
        }
        if (axis === "type") {
            return countLanguageSchools(currentRegionFilter, key);
        }
        if (axis === "univ_type") {
            return countUniversities(currentRegionFilter, key);
        }
        if (axis === "region") {
            const regionKey = key;
            if (currentEntityFilter === "language_schools") {
                return countLanguageSchools(regionKey, currentTypeFilter);
            }
            if (currentEntityFilter === "universities") {
                return countUniversities(regionKey, currentUnivTypeFilter);
            }
            if (currentEntityFilter === "stays") {
                return countStays(regionKey, currentStayTypeFilter);
            }
            return countLanguageSchools(regionKey, "all")
                + countUniversities(regionKey, "all")
                + countStays(regionKey, "all");
        }
        return 0;
    }

    function toggleFilterRows() {
        const schoolRow = document.getElementById("filter-row-school-type");
        const univRow = document.getElementById("filter-row-univ-type");
        const stayRow = document.getElementById("filter-row-stay-type");
        if (!schoolRow || !stayRow) return;

        const showSchool = currentEntityFilter === "language_schools";
        const showUniv = currentEntityFilter === "universities";
        const showStay = currentEntityFilter === "stays";

        schoolRow.classList.toggle("is-hidden", !showSchool);
        schoolRow.setAttribute("aria-hidden", showSchool ? "false" : "true");
        if (univRow) {
            univRow.classList.toggle("is-hidden", !showUniv);
            univRow.setAttribute("aria-hidden", showUniv ? "false" : "true");
        }
        stayRow.classList.toggle("is-hidden", !showStay);
        stayRow.setAttribute("aria-hidden", showStay ? "false" : "true");
    }

    function filterVisibleCards(filteredSchools) {
        // Homepage sections always show all cards; map filters only affect the map.
        if (document.querySelector(".home-sections")) {
            return;
        }

        const ids = new Set(filteredSchools.map((s) => s.id));
        const hideLanguageCards = currentEntityFilter === "stays" || currentEntityFilter === "universities";
        const hideUniversityCards = currentEntityFilter === "stays" || currentEntityFilter === "language_schools";

        document.querySelectorAll(".school-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", hideLanguageCards || !ids.has(card.dataset.schoolId));
        });

        document.querySelectorAll(".university-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", hideUniversityCards || !ids.has(card.dataset.schoolId));
        });

        const stayIds = new Set(currentFilteredStays.map((s) => s.id));
        const hideStayCards = currentEntityFilter === "language_schools" || currentEntityFilter === "universities";
        document.querySelectorAll(".stay-card[data-stay-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", hideStayCards || !stayIds.has(card.dataset.stayId));
        });

        document.querySelectorAll(".card-grid").forEach((grid) => {
            const cards = grid.querySelectorAll(".school-card, .university-card, .stay-card");
            if (!cards.length) return;
            const visibleCount = [...cards].filter((c) => !c.classList.contains("is-filter-hidden")).length;
            grid.classList.toggle("is-filter-empty", visibleCount === 0);
            const sectionHeader = grid.previousElementSibling;
            if (sectionHeader && sectionHeader.classList.contains("section-header")) {
                sectionHeader.classList.toggle("is-filter-empty", visibleCount === 0);
            }
        });
    }

    function updateFilterCounts() {
        document.querySelectorAll(".theme-button[data-filter-axis][data-filter-key]").forEach((btn) => {
            const axis = btn.dataset.filterAxis;
            const key = btn.dataset.filterKey;
            const el = document.getElementById(`count-${axis}-${key}`);
            if (el) el.textContent = String(countForAxis(axis, key));
        });
    }

    function syncActiveButtons() {
        document.querySelectorAll(".theme-button[data-filter-axis]").forEach((btn) => {
            const axis = btn.dataset.filterAxis;
            const key = btn.dataset.filterKey;
            let active = false;
            if (axis === "entity") active = key === currentEntityFilter;
            if (axis === "type") active = key === currentTypeFilter;
            if (axis === "univ_type") active = key === currentUnivTypeFilter;
            if (axis === "stay_type") active = key === currentStayTypeFilter;
            if (axis === "region") active = key === currentRegionFilter;
            btn.classList.toggle("active", active);
        });
    }

    function applyFilters() {
        currentFilteredSchools = computeFilteredSchools();
        currentFilteredStays = computeFilteredStays();
        toggleFilterRows();
        syncActiveButtons();
        filterVisibleCards(currentFilteredSchools);

        document.dispatchEvent(new CustomEvent("jpcampus:filter", {
            detail: {
                entity: currentEntityFilter,
                type: currentTypeFilter,
                univ_type: currentUnivTypeFilter,
                stay_type: currentStayTypeFilter,
                region: currentRegionFilter,
                schools: currentFilteredSchools.slice(),
                stays: currentFilteredStays.slice(),
            },
        }));
    }

    function bootstrap() {
        if (typeof SCHOOLS_DATA !== "undefined") {
            allSchoolData = sortByPublishedDesc(SCHOOLS_DATA.schools || []);
        }
        if (typeof STAYS_DATA !== "undefined") {
            allStayData = sortByPublishedDesc(STAYS_DATA.stays || []);
        }
        updateFilterCounts();
        applyFilters();
    }

    document.addEventListener("click", (event) => {
        const btn = event.target.closest(".theme-button[data-filter-axis][data-filter-key]");
        if (!btn) return;
        event.preventDefault();

        const axis = btn.dataset.filterAxis;
        const key = btn.dataset.filterKey || "all";
        if (axis === "entity") {
            currentEntityFilter = key;
            currentTypeFilter = "all";
            currentUnivTypeFilter = "all";
            currentStayTypeFilter = "all";
        }
        if (axis === "type") currentTypeFilter = key;
        if (axis === "univ_type") currentUnivTypeFilter = key;
        if (axis === "stay_type") currentStayTypeFilter = key;
        if (axis === "region") currentRegionFilter = key;

        updateFilterCounts();
        applyFilters();
    });

    window.JPCampusFilters = {
        applyFilters,
        getCurrentFilteredSchools: () => currentFilteredSchools.slice(),
        getCurrentFilteredStays: () => currentFilteredStays.slice(),
        getCurrentFilteredData: () => currentFilteredSchools.slice(),
        getAllSchoolData: () => allSchoolData.slice(),
        getAllStayData: () => allStayData.slice(),
        getEntityFilter: () => currentEntityFilter,
        getTypeFilter: () => currentTypeFilter,
        getUnivTypeFilter: () => currentUnivTypeFilter,
        getRegionFilter: () => currentRegionFilter,
        refresh: bootstrap,
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootstrap);
    } else {
        bootstrap();
    }
})();
