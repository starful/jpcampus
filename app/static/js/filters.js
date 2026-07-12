/* app/static/js/filters.js — entity (school/stay) + type + region filters */

(function () {
    let allSchoolData = [];
    let allStayData = [];
    let currentEntityFilter = "all";
    let currentTypeFilter = "all";
    let currentStayTypeFilter = "all";
    let currentRegionFilter = "all";
    let currentFilteredSchools = [];
    let currentFilteredStays = [];

    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const DORM_KEYWORDS = ["dormitory", "dorm", "기숙사", "寮", "student housing"];
    const MAJOR_CITIES = ["福岡", "神戸", "札幌", "横浜", "仙台", "Fukuoka", "Kobe", "Sapporo", "Yokohama", "Sendai"];

    function getFeatures(school) {
        const rawFeatures = school.features;
        return Array.isArray(rawFeatures)
            ? rawFeatures.join(" ").toLowerCase()
            : String(rawFeatures || "").toLowerCase();
    }

    function getAddress(item) {
        return item.basic_info?.address || "";
    }

    function matchesSchoolType(school, typeKey) {
        if (typeKey === "university") return school.category === "university";
        if (school.category === "university") return false;
        if (typeKey === "all") return true;

        const features = getFeatures(school);
        const capacity = school.basic_info?.capacity;

        switch (typeKey) {
            case "academic":
                return ACADEMIC_KEYWORDS.some((kw) => features.includes(kw));
            case "dormitory":
                return DORM_KEYWORDS.some((kw) => features.includes(kw));
            case "size_medium":
                return typeof capacity === "number" && capacity > 150 && capacity <= 500;
            default:
                return true;
        }
    }

    function matchesRegion(item, regionKey) {
        if (regionKey === "all") return true;
        const address = getAddress(item);

        switch (regionKey) {
            case "tokyo":
                return address.includes("東京都") || address.includes("Tokyo");
            case "osaka":
                return address.includes("大阪府") || address.includes("Osaka");
            case "nagoya":
                return address.includes("名古屋") || address.includes("愛知") || address.includes("Nagoya");
            case "kyoto":
                return (address.includes("京都") && !address.includes("東京都")) || address.includes("Kyoto");
            case "major_city":
                return !address.includes("東京都")
                    && !address.includes("Tokyo")
                    && !address.includes("大阪府")
                    && !address.includes("名古屋")
                    && !address.includes("愛知")
                    && !(address.includes("京都") && !address.includes("東京都"))
                    && MAJOR_CITIES.some((city) => address.includes(city));
            default:
                return true;
        }
    }

    function matchesStayType(stay, typeKey) {
        if (typeKey === "all") return true;
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
        if (currentEntityFilter === "stays") return [];
        return sortByPublishedDesc(allSchoolData.filter((school) => (
            matchesSchoolType(school, currentTypeFilter) && matchesRegion(school, currentRegionFilter)
        )));
    }

    function computeFilteredStays() {
        if (currentEntityFilter === "schools") return [];
        const typeKey = currentEntityFilter === "stays" ? currentStayTypeFilter : "all";
        return sortByPublishedDesc(allStayData.filter((stay) => (
            matchesStayType(stay, typeKey) && matchesRegion(stay, currentRegionFilter)
        )));
    }

    function countEntity(key) {
        if (key === "all") {
            const s = allSchoolData.filter((x) => matchesSchoolType(x, currentTypeFilter) && matchesRegion(x, currentRegionFilter)).length;
            const t = allStayData.filter((x) => matchesRegion(x, currentRegionFilter)).length;
            return s + t;
        }
        if (key === "schools") {
            return allSchoolData.filter((x) => matchesSchoolType(x, currentTypeFilter) && matchesRegion(x, currentRegionFilter)).length;
        }
        return allStayData.filter((x) => matchesStayType(x, currentStayTypeFilter) && matchesRegion(x, currentRegionFilter)).length;
    }

    function countForAxis(axis, key) {
        if (axis === "entity") return countEntity(key);
        if (axis === "stay_type") {
            return allStayData.filter((x) => matchesStayType(x, key) && matchesRegion(x, currentRegionFilter)).length;
        }
        const typeKey = axis === "type" ? key : currentTypeFilter;
        const regionKey = axis === "region" ? key : currentRegionFilter;
        return allSchoolData.filter((s) => matchesSchoolType(s, typeKey) && matchesRegion(s, regionKey)).length;
    }

    function toggleFilterRows() {
        const schoolRow = document.getElementById("filter-row-school-type");
        const stayRow = document.getElementById("filter-row-stay-type");
        if (!schoolRow || !stayRow) return;

        const showSchool = currentEntityFilter === "all" || currentEntityFilter === "schools";
        const showStay = currentEntityFilter === "stays";

        schoolRow.classList.toggle("is-hidden", !showSchool);
        schoolRow.setAttribute("aria-hidden", showSchool ? "false" : "true");
        stayRow.classList.toggle("is-hidden", !showStay);
        stayRow.setAttribute("aria-hidden", showStay ? "false" : "true");
    }

    function filterVisibleCards(filteredSchools) {
        // Homepage sections always show all cards; map filters only affect the map.
        if (document.querySelector(".home-sections")) {
            return;
        }

        const ids = new Set(filteredSchools.map((s) => s.id));
        const isUniversityFilter = currentTypeFilter === "university";
        const hideSchoolCards = currentEntityFilter === "stays";

        document.querySelectorAll(".school-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", hideSchoolCards || isUniversityFilter || !ids.has(card.dataset.schoolId));
        });

        document.querySelectorAll(".university-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", hideSchoolCards || !isUniversityFilter || !ids.has(card.dataset.schoolId));
        });

        const stayIds = new Set(currentFilteredStays.map((s) => s.id));
        const hideStayCards = currentEntityFilter === "schools";
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
        if (axis === "entity") currentEntityFilter = key;
        if (axis === "type") currentTypeFilter = key;
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
        getRegionFilter: () => currentRegionFilter,
        refresh: bootstrap,
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootstrap);
    } else {
        bootstrap();
    }
})();
