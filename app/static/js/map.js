/* app/static/js/map.js */

let map;
let allSchoolData = [];
let markers = [];
let infoWindow;
let currentFilteredData = [];

// --- [1] 초기화 함수 ---
async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    window.AdvancedMarkerElement = AdvancedMarkerElement;

    map = new Map(document.getElementById("map"), {
        zoom: 6,
        center: { lat: 36.2048, lng: 138.2529 },
        
        // [중요] 제공해주신 mapId 유지
        mapId: "2938bb3f7f034d78c237cb68", 

        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControlOptions: { position: google.maps.ControlPosition.TOP_RIGHT },
    });

    infoWindow = new google.maps.InfoWindow({ minWidth: 280, disableAutoPan: true });

    allSchoolData = SCHOOLS_DATA.schools || [];
    currentFilteredData = allSchoolData;
    bindEvents();
    renderMarkers(allSchoolData);
}

// --- [2] [수정] 이벤트 바인딩 함수 ---
function bindEvents() {
    const dropdown = document.querySelector('.filter-dropdown');
    
    if (dropdown) {
        const trigger = dropdown.querySelector('.dropdown-trigger');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        // 1. 드롭다운 버튼 클릭 (토글)
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('is-open');
        });

        // 2. 메뉴 아이템 클릭 (All 포함 모든 필터 처리)
        menu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation(); // 상위로 클릭 이벤트 전파 방지
                handleTagFilterClick(e); // 필터 처리
                dropdown.classList.remove('is-open'); // 메뉴 닫기
            });
        });

        // 3. 외부 클릭 시 메뉴 닫기
        document.addEventListener('click', () => {
            if (dropdown.classList.contains('is-open')) {
                dropdown.classList.remove('is-open');
            }
        });
    }
    
    // (기존의 별도 '전체 보기' 버튼 이벤트 리스너는 삭제됨)

    // 검색창 이벤트 (기존 유지)
    const univSearchInput = document.getElementById('univ-search-input');
    const clearBtn = document.getElementById('search-clear-btn');
    if (univSearchInput) {
        const runSearch = () => {
            const keyword = (univSearchInput.value || "").trim().toLowerCase();
            if (!keyword) {
                if (currentFilteredData.length) {
                    renderMarkers(currentFilteredData);
                } else {
                    renderMarkers(allSchoolData);
                }
                return;
            }

            const pool = currentFilteredData.length ? currentFilteredData : allSchoolData;
            const found = pool.find(s => {
                const b = s.basic_info || {};
                const candidates = [b.name_en, b.name_ja, b.name_display, s.id]
                    .filter(Boolean)
                    .map(v => String(v).toLowerCase());
                return candidates.some(v => v.includes(keyword));
            });

            if (found && found.location) {
                map.setCenter(found.location);
                map.setZoom(14);
                const marker = markers.find(m => {
                    const title = (m.title || "").toLowerCase();
                    return title === ((found.basic_info?.name_en || found.basic_info?.name_ja || "").toLowerCase());
                });
                if (marker) {
                    openInfoWindow(found, marker);
                }
            }
        };

        univSearchInput.addEventListener('change', runSearch);
        univSearchInput.addEventListener('keydown', (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                runSearch();
            }
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                univSearchInput.value = "";
                renderMarkers(currentFilteredData.length ? currentFilteredData : allSchoolData);
                univSearchInput.focus();
            });
        }
    }
}

// --- [3] [수정] 필터 버튼 클릭 핸들러 ---
function handleTagFilterClick(event) {
    // 클릭된 요소 (dropdown-item)
    const clickedEl = event.currentTarget;
    const filterKey = clickedEl.dataset.filterKey;
    
    // HTML의 data-icon, data-name 속성 가져오기
    const icon = clickedEl.dataset.icon;
    const name = clickedEl.dataset.name;

    // 헤더에 있는 트리거 버튼(표시되는 버튼) 업데이트
    const trigger = document.querySelector('.dropdown-trigger');
    if (trigger) {
        trigger.innerHTML = `${icon} <span class="filter-label" style="margin-left: 8px;">${name}</span>`;
    }
    
    // 필터링 로직 수행
    const filteredSchools = filterSchoolsByKey(filterKey);
    currentFilteredData = filteredSchools;
    renderMarkers(filteredSchools);
}

// --- [4] 필터링 로직 (기존 유지) ---
function filterSchoolsByKey(key) {
    if (key === 'all') return allSchoolData;

    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const BIZ_KEYWORDS = ["business", "job", "취업", "ビジネス"];
    const CULTURE_KEYWORDS = ["conversation", "culture", "short-term", "회화", "短期", "문화"];
    const DORM_KEYWORDS = ['dormitory', '기숙사', '寮'];
    const MAJOR_CITIES = ['福岡', '名古屋', '京都', '神戸', '札幌', '横浜', '仙台'];

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
            case 'major_city': return !address.includes('東京都') && !address.includes('大阪府') && MAJOR_CITIES.some(city => address.includes(city));
            case 'size_small': return typeof capacity === 'number' && capacity <= 150;
            case 'size_medium': return typeof capacity === 'number' && capacity > 150 && capacity <= 500;
            case 'dormitory': return DORM_KEYWORDS.some(kw => features.includes(kw));
            default: return true;
        }
    });
}

// --- [5] [수정] 마커 렌더링 함수 ---
function renderMarkers(data) {
    // 기존 마커 제거
    markers.forEach(m => m.map = null);
    markers = [];

    if (!data || !map || !window.AdvancedMarkerElement) {
        return;
    }

    const bounds = new google.maps.LatLngBounds();

    data.forEach(item => {
        if (!item.location || item.location.lat == null) return;
        
        const isUniv = (item.category === 'university');
        
        // [수정] 이미지 대신 CSS로 스타일링된 HTML 요소 생성
        const markerEl = document.createElement('div');
        
        // 대학이면 주황색 건물 아이콘, 학교면 파란색 학사모 아이콘
        if (isUniv) {
            markerEl.className = 'map-marker marker-univ';
            markerEl.innerHTML = '<i class="fa-solid fa-building-columns"></i>';
        } else {
            markerEl.className = 'map-marker marker-school';
            markerEl.innerHTML = '<i class="fa-solid fa-graduation-cap"></i>';
        }

        // 고급 마커 생성 (content에 HTML 요소 전달)
        const marker = new window.AdvancedMarkerElement({
            map,
            position: item.location,
            title: item.basic_info.name_en || item.basic_info.name_ja,
            content: markerEl, // 이미지가 아닌 div 요소 전달
            zIndex: isUniv ? 100 : 10
        });

        marker.addListener("click", () => openInfoWindow(item, marker));
        markers.push(marker);
        bounds.extend(item.location);
    });

    if (markers.length > 0) {
        if (data.length === allSchoolData.length) {
             // 전체 데이터일 때는 일본 전역 뷰 유지
             // (줌 레벨 변경 없이 map 초기 설정 따름)
        } else {
            if (markers.length === 1) {
                map.setCenter(bounds.getCenter());
                map.setZoom(14);
            } else {
                map.fitBounds(bounds, 100);
                if (map.getZoom() > 15) {
                    map.setZoom(15);
                }
            }
        }
    }
}

// --- [6] 정보창 함수 (기존 유지) ---
function openInfoWindow(school, marker) {
    const isUniv = school.category === 'university';
    const labelColor = isUniv ? 'var(--accent)' : 'var(--primary)';
    const labelText = isUniv ? 'University' : 'Language School';

    if (infoWindow) {
        infoWindow.close();
    }

    infoWindow.setContent(`
        <div class="info-window-content">
            <div class="iw-header">
                <span class="iw-badge" style="background-color: ${labelColor};">${labelText}</span>
                <h5 class="iw-title">${school.basic_info.name_en || school.basic_info.name_ja}</h5>
                <p class="iw-address">${school.basic_info.address || 'Address not available'}</p>
            </div>
            <a href="${school.link}" class="iw-details-btn">View Details →</a>
        </div>`);
    
    infoWindow.open({ anchor: marker, map });
}