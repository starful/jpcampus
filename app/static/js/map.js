/* app/static/js/map.js */

let map;
let schoolMarkers = [];
let univMarkers = [];
let markerCluster;
let infoWindow;

let LatLngBounds; 
let AdvancedMarkerElement; 
let PinElement; 

// [NEW] 1. 커스텀 SVG 아이콘 정의 (직관적이고 깔끔한 벡터 그래픽)
// 어학원용 (주황색, JLS 텍스트)
const SVG_SCHOOL = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 58 84" width="32" height="46">
  <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/>
  </filter>
  <g filter="url(#shadow)">
    <path fill="#E67E22" stroke="#FFFFFF" stroke-width="2" d="M29,0C13,0,0,13,0,29c0,16,29,55,29,55s29-39,29-55C58,13,45,0,29,0z"/>
    <circle cx="29" cy="29" r="18" fill="#FFFFFF" opacity="0.2"/>
    <text x="29" y="36" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">JLS</text>
  </g>
</svg>`;

// 대학용 (파란색, UNI 텍스트)
const SVG_UNIV = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 58 84" width="32" height="46">
  <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/>
  </filter>
  <g filter="url(#shadow)">
    <path fill="#3498DB" stroke="#FFFFFF" stroke-width="2" d="M29,0C13,0,0,13,0,29c0,16,29,55,29,55s29-39,29-55C58,13,45,0,29,0z"/>
    <circle cx="29" cy="29" r="18" fill="#FFFFFF" opacity="0.2"/>
    <text x="29" y="36" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">UNI</text>
  </g>
</svg>`;


async function initMap() {
    console.log("🚀 Google Maps Init Start");

    const { Map } = await google.maps.importLibrary("maps");
    const markerLib = await google.maps.importLibrary("marker");
    AdvancedMarkerElement = markerLib.AdvancedMarkerElement;
    PinElement = markerLib.PinElement;
    
    const coreLib = await google.maps.importLibrary("core");
    LatLngBounds = coreLib.LatLngBounds; 

    const mapOptions = {
        zoom: 12,
        center: { lat: 35.6895, lng: 139.6917 },
        mapId: "2938bb3f7f034d78a2dbaf56", // 사용자의 Map ID
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
    };

    map = new Map(document.getElementById("map"), mapOptions);
    infoWindow = new google.maps.InfoWindow(); 

    // 데이터 확인
    if (typeof SCHOOLS_DATA === 'undefined' || !SCHOOLS_DATA.length) {
        console.warn("⚠️ No school data found.");
        return;
    }

    console.log(`🏫 Rendering ${SCHOOLS_DATA.length} markers...`);

    bindEvents();
    renderMarkers(SCHOOLS_DATA);
}

function bindEvents() {
    // Select 박스 변경 시
    document.querySelectorAll('.search-container select').forEach(select => {
        select.addEventListener('change', () => {
            updateFilterUI();
        });
    });

    // 검색창 입력 시
    const univInput = document.getElementById("filter-univ");
    if (univInput) {
        univInput.addEventListener('keypress', (e) => {
             if (e.key === 'Enter') applyFilters();
        });
        univInput.addEventListener('input', () => {
             updateFilterUI();
        });
    }
    
    // 검색 버튼 클릭 시
    const searchBtn = document.getElementById("search-btn");
    if (searchBtn) {
        searchBtn.addEventListener("click", applyFilters);
    }
}

function updateFilterUI() {
    document.querySelectorAll('.search-container select').forEach(sel => {
        if (sel.value !== 'all') sel.classList.add('active-filter');
        else sel.classList.remove('active-filter');
    });

    const input = document.getElementById("filter-univ");
    if (input) {
        if (input.value.trim() !== "") input.classList.add('active-filter');
        else input.classList.remove('active-filter');
    }
}

function toggleButtons(isFiltered) {
    return; 
}

// [중요] 렌더링 함수 수정 (SVG 적용)
function renderMarkers(data) {
    if (!map || !LatLngBounds || !AdvancedMarkerElement) {
        console.warn("⚠️ Maps library not loaded yet.");
        return;
    }

    if (markerCluster) markerCluster.clearMarkers();
    
    schoolMarkers.forEach(m => m.map = null);
    univMarkers.forEach(m => m.map = null);
    
    schoolMarkers = [];
    univMarkers = [];

    const bounds = new LatLngBounds();
    const parser = new DOMParser(); // SVG 문자열을 DOM 요소로 변환하기 위함

    data.forEach(item => {
        // 숫자 ID 제외 (구형 데이터 방지)
        if (/^\d+$/.test(item.id)) return;

        if (!item.location || !item.location.lat) return;
        const position = { lat: item.location.lat, lng: item.location.lng };
        
        // [NEW] SVG 문자열 선택 및 DOM 요소 변환
        const isUniv = (item.category === 'university');
        const svgString = isUniv ? SVG_UNIV : SVG_SCHOOL;
        
        // SVG 문자열을 HTML Element로 파싱
        const pinContent = parser.parseFromString(svgString, 'image/svg+xml').documentElement;
        
        // AdvancedMarkerElement 생성
        const marker = new AdvancedMarkerElement({
            map: map,
            position: position,
            title: item.basic_info.name_ja,
            content: pinContent, // SVG 요소를 컨텐츠로 설정
            zIndex: isUniv ? 9999 : 1, // 대학을 위로 올림
        });

        marker.addListener("click", () => openInfoWindow(item, marker));

        if (isUniv) {
            univMarkers.push(marker); 
        } else {
            schoolMarkers.push(marker);
        }
        bounds.extend(position);
    });

    // 결과 수 업데이트
    const countEl = document.getElementById("result-count");
    if (countEl) countEl.innerText = schoolMarkers.length + univMarkers.length;

    if (!window.isSearchMove && (schoolMarkers.length + univMarkers.length) > 0) {
         map.fitBounds(bounds);
    }
}


// 정보창 함수
function openInfoWindow(school, marker) {
    const detailUrl = school.link || `/school/${school.id}`;
    
    const websiteUrl = (school.category === 'university' && school.basic_info.website) 
        ? school.basic_info.website 
        : (school.source_url || '#');

    const labelColor = school.category === 'university' ? '#3498DB' : '#E67E22'; // 핀 색상과 일치
    const labelText = school.category === 'university' ? 'UNIVERSITY' : 'LANGUAGE SCHOOL';
    
    // 이모지는 유지하되 색상 테마 통일
    const icon = school.category === 'university' ? '🎓' : '🏫';

    const contentString = `
        <div class="info-window-card">
            <div class="iw-header" style="border-left: 5px solid ${labelColor}; padding-left:15px; margin-bottom:10px;">
                <span style="font-size:0.75rem; font-weight:bold; color:${labelColor}; display:block; margin-bottom:4px; letter-spacing:1px;">
                    ${labelText}
                </span>
                <a href="${detailUrl}" class="iw-title" style="color:#333; font-size:1.1rem; text-decoration:none; display:block;">
                    ${school.basic_info.name_ja}
                </a>
            </div>
            
            <div class="iw-body">
                <div class="iw-row">
                    <i class="fas fa-map-marker-alt iw-icon"></i>
                    <span>${school.basic_info.address}</span>
                </div>
                ${school.basic_info.capacity ? `
                <div class="iw-row">
                    <i class="fas fa-users iw-icon"></i>
                    <span>Capacity: ${school.basic_info.capacity}</span>
                </div>` : ''}
                
                <a href="${detailUrl}" class="iw-btn" style="background-color: ${labelColor}; color: white;">
                    View Details
                </a>

                ${websiteUrl !== '#' ? `
                <a href="${websiteUrl}" target="_blank" class="iw-btn" style="background-color: #f8f9fa; color: #555; border: 1px solid #ddd; margin-top: 8px;">
                    Official Website <i class="fas fa-external-link-alt"></i>
                </a>
                ` : ''}
            </div>
        </div>
    `;

    infoWindow.setContent(contentString);
    infoWindow.open(map, marker);
}

// [검색] 매칭 헬퍼
function checkNameMatch(item, query) {
    if (!query) return false;
    query = query.toLowerCase().replace(/\s+/g, '');
    
    const nameJa = (item.basic_info.name_ja || "").toLowerCase().replace(/\s+/g, '');
    const nameEn = (item.basic_info.name_en || "").toLowerCase().replace(/\s+/g, '');
    const id = (item.id || "").toLowerCase();

    if (nameJa.includes(query)) return true;
    if (nameEn.includes(query)) return true;
    if (id.includes(query)) return true;
    
    if (item.career_path && item.career_path.major_universities) {
        let keywords = [query];
        if (query.includes('waseda') || query.includes('와세다')) keywords.push('早稲田');
        if (query.includes('keio') || query.includes('게이오')) keywords.push('慶應');
        if (query.includes('meiji') || query.includes('메이지')) keywords.push('明治');
        if (query.includes('tokyo') || query.includes('도쿄')) keywords.push('東京');
        
        return item.career_path.major_universities.some(univ => 
            keywords.some(k => univ.toLowerCase().includes(k))
        );
    }
    return false;
}

// [검색] 필터 적용 함수
function applyFilters() {
    const univInputEl = document.getElementById("filter-univ");
    const univInput = univInputEl ? univInputEl.value.trim().toLowerCase() : "";
    
    const region = document.getElementById("filter-region")?.value || "all";
    const price = document.getElementById("filter-price")?.value || "all";
    const nation = document.getElementById("filter-nation")?.value || "all";
    const scale = document.getElementById("filter-scale")?.value || "all";
    const career = document.getElementById("filter-career")?.value || "all";
    const special = document.getElementById("filter-special")?.value || "all";
    const dorm = document.getElementById("filter-dorm")?.value || "all";
    const scholarship = document.getElementById("filter-scholarship")?.value || "all";
    const eju = document.getElementById("filter-eju")?.value || "all";
    const convo = document.getElementById("filter-convo")?.value || "all";
    const env = document.getElementById("filter-env")?.value || "all";

    console.log(`🔍 Searching for: "${univInput}"`);

    let targetUnivLocation = null;
    if (univInput !== "") {
        const targetUniv = SCHOOLS_DATA.find(s => 
            s.category === 'university' && checkNameMatch(s, univInput)
        );
        if (targetUniv && targetUniv.location) {
            targetUnivLocation = targetUniv.location;
        }
    }

    const filtered = SCHOOLS_DATA.filter(s => {
        if (s.category === 'university') {
            if (univInput !== "") return checkNameMatch(s, univInput);
            return false; 
        }

        const addr = s.basic_info.address || "";
        const feats = (s.features || []).join(" ");
        const cNames = (s.courses || []).map(c => c.course_name).join(" ");
        const cap = s.basic_info.capacity || 0;
        
        if (region !== "all" && !addr.includes(region)) return false;

        if (univInput !== "") {
            if (!checkNameMatch(s, univInput)) return false; 
        }
        
        if (price !== "all") {
             const fees = (s.courses || []).map(c => c.total_fees).filter(f => typeof f === 'number');
             if (fees.length === 0 || Math.min(...fees) > parseInt(price) * 10000) return false;
        }

        if (nation !== "all") {
            const demo = s.student_demographics || {};
            const total = demo.total || 0;
            if (total === 0) return false;
            
            const krRatio = (demo.korea || 0) / total;
            const westRatio = (demo.usa || 0) / total; 
            const cnRatio = (demo.china || 0) / total;
            const vnRatio = (demo.vietnam || 0) / total;

            if (nation === "global" && westRatio < 0.1) return false;
            if (nation === "korea_low" && krRatio > 0.3) return false;
            if (nation === "china_high" && cnRatio < 0.5) return false;
            if (nation === "vietnam_high" && vnRatio < 0.3) return false;
        }

        if (scale !== "all") {
            if (scale === "large" && cap < 500) return false;
            if (scale === "medium" && (cap < 200 || cap >= 500)) return false;
            if (scale === "small" && cap >= 200) return false;
        }

        if (career !== "all") {
            const cp = s.career_path || {};
            if (career === "grad_school" && (cp.grad_school || 0) < 5) return false;
            if (career === "university" && (cp.university || 0) < 10) return false;
            if (career === "vocational" && (cp.vocational || 0) < 10) return false;
        }

        if (special !== "all") {
            if (special === "art" && !feats.includes("미술") && !feats.includes("디자인")) return false;
            if (special === "biz" && !feats.includes("비즈니스") && !feats.includes("취업")) return false;
            if (special === "jlpt" && !cNames.includes("N1") && !feats.includes("JLPT")) return false;
            if (special === "short" && !cNames.includes("단기")) return false;
        }

        if (dorm !== "all") {
            if (dorm === "yes" && !feats.includes("기숙사")) return false;
            if (dorm === "single" && !feats.includes("1인실")) return false;
            if (dorm === "school_owned" && !feats.includes("기숙사")) return false;
        }

        if (scholarship !== "all") {
            if (!feats.includes("장학금")) return false;
        }

        if (eju !== "all") {
            if (eju === "yes" && !feats.includes("EJU")) return false;
            if (eju === "science" && !feats.includes("이과")) return false;
            if (eju === "art" && !feats.includes("미술")) return false;
        }

        if (convo !== "all") {
            if (convo === "yes" && !feats.includes("회화")) return false;
        }

        if (env !== "all") {
            const isBusy = addr.includes("新宿") || addr.includes("渋谷") || addr.includes("池袋");
            if (env === "quiet" && isBusy) return false;
            if (env === "active" && !isBusy) return false;
        }
        
        return true;
    });

    console.log(`✅ Result: ${filtered.length} schools found.`);

    window.isSearchMove = !!(targetUnivLocation && univInput !== "");
    
    renderMarkers(filtered);

    if (targetUnivLocation) {
        map.panTo(targetUnivLocation);
        map.setZoom(14);
    }

    updateFilterUI();
    toggleButtons(true);
}

function resetFilters() {
    document.querySelectorAll(".search-container select").forEach(el => el.value = 'all');
    const univInput = document.getElementById("filter-univ");
    if(univInput) univInput.value = "";
    
    window.isSearchMove = false;
    
    renderMarkers(SCHOOLS_DATA);
    updateFilterUI();
    toggleButtons(false);
}

window.initMap = initMap;