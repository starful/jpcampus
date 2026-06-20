/* app/static/js/filters.js — two-axis combo filters (type + region) */

(function () {
    let allSchoolData = [];
    let currentTypeFilter = "all";
    let currentRegionFilter = "all";
    let currentFilteredData = [];

    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const DORM_KEYWORDS = ["dormitory", "dorm", "기숙사", "寮", "student housing"];
    const MAJOR_CITIES = ["福岡", "神戸", "札幌", "横浜", "仙台", "Fukuoka", "Kobe", "Sapporo", "Yokohama", "Sendai"];

    function getFeatures(school) {
        const rawFeatures = school.features;
        return Array.isArray(rawFeatures)
            ? rawFeatures.join(" ").toLowerCase()
            : String(rawFeatures || "").toLowerCase();
    }

    function getAddress(school) {
        return school.basic_info?.address || "";
    }

    function matchesType(school, typeKey) {
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

    function matchesRegion(school, regionKey) {
        if (regionKey === "all") return true;
        const address = getAddress(school);

        switch (regionKey) {
            case "tokyo":
                return address.includes("東京都");
            case "osaka":
                return address.includes("大阪府");
            case "nagoya":
                return address.includes("名古屋") || address.includes("愛知");
            case "kyoto":
                return address.includes("京都") && !address.includes("東京都");
            case "major_city":
                return !address.includes("東京都")
                    && !address.includes("大阪府")
                    && !address.includes("名古屋")
                    && !address.includes("愛知")
                    && !(address.includes("京都") && !address.includes("東京都"))
                    && MAJOR_CITIES.some((city) => address.includes(city));
            default:
                return true;
        }
    }

    function computeFilteredData(typeKey = currentTypeFilter, regionKey = currentRegionFilter) {
        return allSchoolData.filter((school) => (
            matchesType(school, typeKey) && matchesRegion(school, regionKey)
        ));
    }

    function countForAxis(axis, key) {
        const typeKey = axis === "type" ? key : currentTypeFilter;
        const regionKey = axis === "region" ? key : currentRegionFilter;
        return computeFilteredData(typeKey, regionKey).length;
    }

    function filterVisibleCards(filteredSchools) {
        const ids = new Set(filteredSchools.map((s) => s.id));
        const isUniversityFilter = currentTypeFilter === "university";

        document.querySelectorAll(".school-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", isUniversityFilter || !ids.has(card.dataset.schoolId));
        });

        document.querySelectorAll(".university-card[data-school-id]").forEach((card) => {
            card.classList.toggle("is-filter-hidden", !isUniversityFilter || !ids.has(card.dataset.schoolId));
        });

        document.querySelectorAll(".card-grid").forEach((grid) => {
            const schoolCards = grid.querySelectorAll(".school-card[data-school-id]");
            const univCards = grid.querySelectorAll(".university-card[data-school-id]");
            const cards = schoolCards.length ? schoolCards : univCards;
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
        document.querySelectorAll('.theme-button[data-filter-axis="type"]').forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.filterKey === currentTypeFilter);
        });
        document.querySelectorAll('.theme-button[data-filter-axis="region"]').forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.filterKey === currentRegionFilter);
        });
    }

    function applyFilters() {
        currentFilteredData = computeFilteredData();
        syncActiveButtons();
        filterVisibleCards(currentFilteredData);

        document.dispatchEvent(new CustomEvent("jpcampus:filter", {
            detail: {
                type: currentTypeFilter,
                region: currentRegionFilter,
                schools: currentFilteredData.slice(),
            },
        }));
    }

    function bootstrap() {
        if (typeof SCHOOLS_DATA !== "undefined") {
            allSchoolData = SCHOOLS_DATA.schools || [];
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
        if (axis === "type") currentTypeFilter = key;
        if (axis === "region") currentRegionFilter = key;

        updateFilterCounts();
        applyFilters();
    });

    window.JPCampusFilters = {
        applyFilters,
        getCurrentFilteredData: () => currentFilteredData.slice(),
        getAllSchoolData: () => allSchoolData.slice(),
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
