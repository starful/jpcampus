/* app/static/js/filters.js — map-independent category filters */

(function () {
    let allSchoolData = [];
    let currentFilterKey = 'all';
    let currentFilteredData = [];

    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const BIZ_KEYWORDS = ["business", "job", "취업", "ビジネス"];
    const CULTURE_KEYWORDS = ["conversation", "culture", "short-term", "회화", "短期", "문화"];
    const DORM_KEYWORDS = ['dormitory', 'dorm', '기숙사', '寮', 'student housing'];
    const MAJOR_CITIES = ['福岡', '名古屋', '京都', '神戸', '札幌', '横浜', '仙台', 'Fukuoka', 'Nagoya', 'Kyoto', 'Kobe', 'Sapporo', 'Yokohama', 'Sendai'];

    function filterSchoolsByKey(key) {
        if (key === 'university') return allSchoolData.filter(s => s.category === 'university');
        if (key === 'all') return allSchoolData.filter(s => s.category !== 'university');

        return allSchoolData.filter(school => {
            if (school.category === 'university') return false;

            const rawFeatures = school.features;
            const features = Array.isArray(rawFeatures)
                ? rawFeatures.join(" ").toLowerCase()
                : String(rawFeatures || "").toLowerCase();
            const address = school.basic_info?.address || '';
            const capacity = school.basic_info?.capacity;

            switch (key) {
                case 'academic': return ACADEMIC_KEYWORDS.some(kw => features.includes(kw));
                case 'business': return BIZ_KEYWORDS.some(kw => features.includes(kw));
                case 'culture': return CULTURE_KEYWORDS.some(kw => features.includes(kw));
                case 'tokyo': return address.includes('東京都');
                case 'osaka': return address.includes('大阪府');
                case 'major_city':
                    return !address.includes('東京都') && !address.includes('大阪府')
                        && MAJOR_CITIES.some(city => address.includes(city));
                case 'size_small': return typeof capacity === 'number' && capacity <= 150;
                case 'size_medium': return typeof capacity === 'number' && capacity > 150 && capacity <= 500;
                case 'dormitory': return DORM_KEYWORDS.some(kw => features.includes(kw));
                default: return true;
            }
        });
    }

    function filterVisibleCards(filteredSchools) {
        const ids = new Set(filteredSchools.map(s => s.id));
        document.querySelectorAll('.school-card[data-school-id]').forEach(card => {
            card.classList.toggle('is-filter-hidden', !ids.has(card.dataset.schoolId));
        });

        document.querySelectorAll('.card-grid').forEach(grid => {
            const cards = grid.querySelectorAll('.school-card[data-school-id]');
            if (!cards.length) return;
            const visibleCount = [...cards].filter(c => !c.classList.contains('is-filter-hidden')).length;
            grid.classList.toggle('is-filter-empty', visibleCount === 0);
            const sectionHeader = grid.previousElementSibling;
            if (sectionHeader && sectionHeader.classList.contains('section-header')) {
                sectionHeader.classList.toggle('is-filter-empty', visibleCount === 0);
            }
        });
    }

    function updateFilterCounts() {
        document.querySelectorAll('.theme-button[data-filter-key]').forEach(btn => {
            const key = btn.dataset.filterKey;
            const el = document.getElementById(`count-${key}`);
            if (el) el.textContent = String(filterSchoolsByKey(key).length);
        });
    }

    function applyFilterKey(filterKey) {
        currentFilterKey = filterKey || 'all';
        currentFilteredData = filterSchoolsByKey(currentFilterKey);

        document.querySelectorAll('.theme-button[data-filter-key]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filterKey === currentFilterKey);
        });

        filterVisibleCards(currentFilteredData);

        document.dispatchEvent(new CustomEvent('jpcampus:filter', {
            detail: { key: currentFilterKey, schools: currentFilteredData.slice() }
        }));
    }

    function bootstrap() {
        if (typeof SCHOOLS_DATA !== 'undefined') {
            allSchoolData = SCHOOLS_DATA.schools || [];
        }
        updateFilterCounts();
        applyFilterKey(currentFilterKey);
    }

    document.addEventListener('click', (event) => {
        const btn = event.target.closest('.theme-button[data-filter-key]');
        if (!btn) return;
        event.preventDefault();
        applyFilterKey(btn.dataset.filterKey || 'all');
    });

    window.JPCampusFilters = {
        applyFilterKey,
        filterSchoolsByKey,
        getCurrentFilteredData: () => currentFilteredData.slice(),
        getAllSchoolData: () => allSchoolData.slice(),
        refresh: bootstrap,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootstrap);
    } else {
        bootstrap();
    }
})();
