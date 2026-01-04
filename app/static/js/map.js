/* app/static/js/map.js */

let map;
let allSchoolData = [];
let markers = [];
let infoWindow;

// --- [1] 초기화 함수 ---
async function initMap() {
    // 필요한 구글맵 라이브러리를 비동기적으로 로드합니다.
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    window.AdvancedMarkerElement = AdvancedMarkerElement; // 다른 함수에서 쓸 수 있도록 전역 할당

    map = new Map(document.getElementById("map"), {
        zoom: 5,
        center: { lat: 36, lng: 138 }, // 일본 중앙으로 중심점 조정
        mapId: "2938bb3f7f034d78",
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControlOptions: { position: google.maps.ControlPosition.TOP_RIGHT },
    });

    infoWindow = new google.maps.InfoWindow({ minWidth: 280, disableAutoPan: true });

    allSchoolData = SCHOOLS_DATA.schools || [];
    bindEvents();
    renderMarkers(allSchoolData); // 초기에는 모든 마커 표시
}

// --- [2] 이벤트 바인딩 함수 ---
function bindEvents() {
    document.querySelectorAll('.tag-filter-btn').forEach(button => {
        button.addEventListener('click', handleTagFilterClick);
    });
    // 검색 기능은 현재 로직을 유지합니다.
    const univSearchInput = document.getElementById('univ-search-input');
    if (univSearchInput) {
        // ... (검색 관련 이벤트 리스너는 기존과 동일)
    }
}

// --- [3] 필터 버튼 클릭 핸들러 ---
function handleTagFilterClick(event) {
    const clickedButton = event.currentTarget;
    const filterKey = clickedButton.dataset.filterKey;

    document.querySelectorAll('.tag-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    clickedButton.classList.add('active');

    // [핵심] 수정된 필터링 함수를 호출합니다.
    const filteredSchools = filterSchoolsByKey(filterKey);
    renderMarkers(filteredSchools);
}

// --- [4] [핵심 수정] 새로운 기준을 반영한 필터링 로직 ---
function filterSchoolsByKey(key) {
    if (key === 'all') {
        return allSchoolData;
    }

    // Python(utils.py)의 로직을 JavaScript로 동일하게 구현
    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const BIZ_KEYWORDS = ["business", "job", "취업", "ビジネス"];
    const CULTURE_KEYWORDS = ["conversation", "culture", "short-term", "회화", "短期", "문화"];
    const DORM_KEYWORDS = ['dormitory', '기숙사', '寮'];
    const MAJOR_CITIES = ['福岡', '名古屋', '京都', '神戸', '札幌', '横浜', '仙台'];

    return allSchoolData.filter(school => {
        // 대학은 필터링 대상에서 항상 제외
        if (school.category === 'university') return false;

        // 필터링에 필요한 데이터 안전하게 추출
        const features = (school.features || []).join(" ").toLowerCase();
        const address = school.basic_info?.address || '';
        const capacity = school.basic_info?.capacity;

        switch (key) {
            // 기존 필터
            case 'academic':
                return ACADEMIC_KEYWORDS.some(kw => features.includes(kw));
            case 'business':
                return BIZ_KEYWORDS.some(kw => features.includes(kw));
            case 'culture':
                return CULTURE_KEYWORDS.some(kw => features.includes(kw));

            // 신규 필터
            case 'tokyo':
                return address.includes('東京都');
            case 'osaka':
                return address.includes('大阪府');
            case 'major_city':
                // 도쿄, 오사카가 아니면서 주요 도시에 포함되는 경우
                return !address.includes('東京都') && !address.includes('大阪府') && MAJOR_CITIES.some(city => address.includes(city));
            
            case 'size_small':
                return typeof capacity === 'number' && capacity <= 150;
            case 'size_medium':
                return typeof capacity === 'number' && capacity > 150 && capacity <= 500;

            case 'dormitory':
                return DORM_KEYWORDS.some(kw => features.includes(kw));

            default:
                return true; // 알 수 없는 필터키의 경우 모두 표시 (안전장치)
        }
    });
}

// --- [5] 마커 렌더링 함수 (아이콘 방식 간소화) ---
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
        
        // 아이콘을 SVG 문자열 대신 이미지 파일로 교체하여 단순화
        const markerIcon = document.createElement('img');
        markerIcon.src = isUniv ? '/static/img/pin-univ.png' : '/static/img/pin-school.png';
        markerIcon.style.width = '32px';
        markerIcon.style.height = '46px';
        markerIcon.style.cursor = 'pointer';

        const marker = new window.AdvancedMarkerElement({
            map,
            position: item.location,
            title: item.basic_info.name_en || item.basic_info.name_ja,
            content: markerIcon,
            zIndex: isUniv ? 100 : 10 // 대학 마커가 항상 위에 오도록 z-index 설정
        });

        marker.addListener("click", () => openInfoWindow(item, marker));
        markers.push(marker);
        bounds.extend(item.location);
    });

    if (markers.length > 0) {
        if (markers.length === 1) {
            map.setCenter(bounds.getCenter());
            map.setZoom(14);
        } else {
            // 지도가 너무 확대되지 않도록 최대 줌 레벨 설정
            map.fitBounds(bounds, 100); // 100px padding
            if (map.getZoom() > 15) {
                map.setZoom(15);
            }
        }
    }
}

// --- [6] 정보창 함수 (UI 개선 버전 유지) ---
function openInfoWindow(school, marker) {
    const isUniv = school.category === 'university';
    const labelColor = isUniv ? 'var(--accent)' : 'var(--primary)';
    const labelText = isUniv ? 'University' : 'Language School';

    const contentString = `
        <div class="info-window-content">
            <div class="iw-header">
                <span class="iw-badge" style="background-color: ${labelColor};">${labelText}</span>
                <h5 class="iw-title">${school.basic_info.name_en || school.basic_info.name_ja}</h5>
                <p class="iw-address">${school.basic_info.address || 'Address not available'}</p>
            </div>
            <a href="${school.link}" class="iw-details-btn">View Details →</a>
        </div>`;

    if (infoWindow) {
        infoWindow.close();
    }
    
    infoWindow.setContent(contentString);
    infoWindow.open({ anchor: marker, map });
}