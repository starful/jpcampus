/* app/static/js/map.js */

let map;
let schoolMarkers = [];
let univMarkers = [];
let markerCluster;
let infoWindow;
let ICONS = {}; 

// 초기화 함수
function initMap() {
    console.log("🚀 Google Maps Init Start");
    
    // 1. 아이콘 설정 (구글 객체 로드 후 실행)
    ICONS = {
        university: {
            url: "/static/img/pin-univ.png",
            scaledSize: new google.maps.Size(64, 64),
            anchor: new google.maps.Point(32, 64)
        },
        school: {
            url: "/static/img/pin-school.png",
            scaledSize: new google.maps.Size(50, 50),
            anchor: new google.maps.Point(25, 50)
        }
    };

    // 2. 지도 생성
    const japanCenter = { lat: 36.2048, lng: 138.2529 }; 
    map = new google.maps.Map(document.getElementById("map"), {
        center: japanCenter,
        zoom: 5,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        styles: [{ "featureType": "poi", "elementType": "labels", "stylers": [{ "visibility": "off" }] }]
    });

    infoWindow = new google.maps.InfoWindow({ maxWidth: 320 });

    // 3. 데이터 렌더링
    if (typeof SCHOOLS_DATA !== 'undefined' && SCHOOLS_DATA.length > 0) {
        console.log(`🏫 Rendering ${SCHOOLS_DATA.length} markers...`);
        renderMarkers(SCHOOLS_DATA);
    } else {
        console.warn("⚠️ No SCHOOLS_DATA found.");
    }
    
    // 4. 이벤트 바인딩
    bindEvents();

    // 5. 초기 버튼 상태 (Search 버튼 보이기)
    toggleButtons(false);
}

function bindEvents() {
    // Select 박스 변경 시
    document.querySelectorAll('.search-container select').forEach(select => {
        select.addEventListener('change', () => {
            updateFilterUI();
            // 자동 검색을 원하면 아래 주석 해제
            // applyFilters(); 
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
    const searchBtn = document.getElementById("search-btn");
    const resetBtn = document.getElementById("reset-btn");
    
    if (searchBtn && resetBtn) {
        if (isFiltered) {
            searchBtn.style.display = "none";
            resetBtn.style.display = "block"; // 혹은 inline-block
        } else {
            searchBtn.style.display = "block"; // 혹은 inline-block
            resetBtn.style.display = "none";
        }
    }
}

// 마커 그리기 함수
function renderMarkers(data) {
    // 초기화
    if (markerCluster) markerCluster.clearMarkers();
    schoolMarkers.forEach(m => m.setMap(null));
    univMarkers.forEach(m => m.setMap(null));
    schoolMarkers = [];
    univMarkers = [];

    const bounds = new google.maps.LatLngBounds();
    const lang = (typeof currentLang !== 'undefined') ? currentLang : 'en';
    const t = (typeof translations !== 'undefined' && translations[lang]) ? translations[lang] : (translations['en'] || {});

    data.forEach(item => {
        if (!item.location || !item.location.lat) return;
        const position = { lat: item.location.lat, lng: item.location.lng };
        
        // 이름 언어 설정
        let dispName = item.basic_info.name_ja;
        if (lang === 'en' && item.basic_info.name_en) {
            dispName = item.basic_info.name_en;
        }

        // [A] 대학 마커
        if (item.category === 'university') {
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: dispName,
                zIndex: 9999,
                icon: ICONS.university,
            });

            marker.addListener("click", () => {
                const content = `
                <div class="info-window-card">
                    <div class="iw-header" style="background:#0F4C81;">
                        <a href="/school/${item.id}" class="iw-title">🎓 ${dispName}</a>
                    </div>
                    <div class="iw-body">
                        <div class="iw-row"><i class="fas fa-map-marker-alt iw-icon"></i> ${item.basic_info.address}</div>
                        <a href="${item.basic_info.website}" target="_blank" class="iw-btn" style="background:#0F4C81;">${t.iw_univ_home || 'Website'}</a>
                    </div>
                </div>`;
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            });
            univMarkers.push(marker); 
            bounds.extend(position);
        } 
        // [B] 어학원 마커
        else {
            const fees = item.courses ? item.courses.map(c => c.total_fees || 9999999) : [];
            const minFee = Math.min(...fees);
            let feeText = '-';
            if (minFee !== 9999999) {
                if(lang === 'en') feeText = "¥" + (minFee/10000).toLocaleString() + "0k";
                else feeText = (minFee/10000).toLocaleString() + (t.unit_money || '만엔');
            }

            const marker = new google.maps.Marker({
                position: position,
                title: dispName,
                zIndex: 1,
                icon: ICONS.school
            });

            marker.addListener("click", () => {
                const featureTags = (item.features || []).slice(0, 3).map(f => `<span class="iw-tag">${f}</span>`).join('');
                const content = `
                <div class="info-window-card">
                    <div class="iw-header" style="background:#F28C28;">
                        <a href="/school/${item.id}" class="iw-title">🏫 ${dispName}</a>
                    </div>
                    <div class="iw-body">
                        <div class="iw-row"><i class="fas fa-map-marker-alt iw-icon"></i> ${item.basic_info.address}</div>
                        <div class="iw-row"><i class="fas fa-users iw-icon"></i> ${t.iw_capacity || 'Cap'}: ${item.basic_info.capacity}</div>
                        <div class="iw-row"><i class="fas fa-yen-sign iw-icon"></i> ${feeText}</div>
                        <div class="iw-tags">${featureTags}</div>
                        <a href="/school/${item.id}" class="iw-btn" style="background:#F28C28;">${t.iw_school_detail || 'Details'}</a>
                    </div>
                </div>`;
                infoWindow.setContent(content);
                infoWindow.open(map, marker);
            });
            schoolMarkers.push(marker);
            bounds.extend(position);
        }
    });

    // 클러스터링 적용
    if (typeof markerClusterer !== 'undefined') {
        markerCluster = new markerClusterer.MarkerClusterer({ markers: schoolMarkers, map: map });
    }

    // 결과 개수 업데이트
    const countEl = document.getElementById("result-count");
    if (countEl) countEl.innerText = schoolMarkers.length + univMarkers.length;

    // 지도 범위 자동 조정 (검색 이동이 아닐 때만)
    if (!window.isSearchMove && (schoolMarkers.length + univMarkers.length) > 0) {
         map.fitBounds(bounds);
    }
}

// 검색어 매칭 헬퍼 함수
function checkNameMatch(item, query) {
    if (!query) return false;
    query = query.toLowerCase();
    
    // 기본 이름 확인
    if (item.basic_info.name_ja && item.basic_info.name_ja.toLowerCase().includes(query)) return true;
    if (item.basic_info.name_en && item.basic_info.name_en.toLowerCase().includes(query)) return true;
    
    // 진학 실적 확인
    if (item.career_path && item.career_path.major_universities) {
        let keywords = [query];
        // 간이 번역 매핑
        if (query.includes('waseda')) keywords.push('早稲田');
        if (query.includes('keio')) keywords.push('慶應');
        if (query.includes('meiji')) keywords.push('明治');
        if (query.includes('tokyo')) keywords.push('東京');
        
        return item.career_path.major_universities.some(univ => 
            keywords.some(k => univ.toLowerCase().includes(k))
        );
    }
    return false;
}

// 필터 적용 함수 (생략 없이 전체 구현)
function applyFilters() {
    // 1. 모든 필터 값 가져오기
    const region = document.getElementById("filter-region")?.value || "all";
    const univInput = document.getElementById("filter-univ")?.value.trim().toLowerCase() || "";
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

    // 2. 대학 검색 시 해당 대학 좌표 찾기
    let targetUnivLocation = null;
    if (univInput !== "") {
        const targetUniv = SCHOOLS_DATA.find(s => 
            s.category === 'university' && checkNameMatch(s, univInput)
        );
        if (targetUniv && targetUniv.location) {
            targetUnivLocation = targetUniv.location;
        }
    }

    // 3. 필터링 실행
    const filtered = SCHOOLS_DATA.filter(s => {
        // [A] 대학인 경우
        if (s.category === 'university') {
            if (univInput !== "") return checkNameMatch(s, univInput);
            return false; // 검색어 없으면 대학 핀 숨김
        }

        // [B] 어학원인 경우
        const addr = s.basic_info.address || "";
        const feats = (s.features || []).join(" ");
        const cNames = (s.courses || []).map(c => c.course_name).join(" ");
        const cap = s.basic_info.capacity || 0;
        
        // 지역 필터
        if (region !== "all" && !addr.includes(region)) return false;

        // 대학 검색 필터 (진학 실적)
        if (univInput !== "") {
            if (!checkNameMatch(s, univInput)) return false; 
        }
        
        // 학비 필터
        if (price !== "all") {
             const fees = (s.courses || []).map(c => c.total_fees).filter(f => typeof f === 'number');
             if (fees.length === 0 || Math.min(...fees) > parseInt(price) * 10000) return false;
        }

        // 국적 필터
        if (nation !== "all") {
            const demo = s.student_demographics || {};
            const total = demo.total || 0;
            if (total === 0) return false;
            
            const krRatio = (demo.korea || 0) / total;
            const westRatio = (demo.usa || 0) / total; // 예시
            const cnRatio = (demo.china || 0) / total;
            const vnRatio = (demo.vietnam || 0) / total;

            if (nation === "global" && westRatio < 0.1) return false;
            if (nation === "korea_low" && krRatio > 0.3) return false;
            if (nation === "china_high" && cnRatio < 0.5) return false;
            if (nation === "vietnam_high" && vnRatio < 0.3) return false;
        }

        // 규모 필터
        if (scale !== "all") {
            if (scale === "large" && cap < 500) return false;
            if (scale === "medium" && (cap < 200 || cap >= 500)) return false;
            if (scale === "small" && cap >= 200) return false;
        }

        // 진학 필터
        if (career !== "all") {
            const cp = s.career_path || {};
            if (career === "grad_school" && (cp.grad_school || 0) < 5) return false;
            if (career === "university" && (cp.university || 0) < 10) return false;
            if (career === "vocational" && (cp.vocational || 0) < 10) return false;
        }

        // 특화 필터
        if (special !== "all") {
            if (special === "art" && !feats.includes("미술") && !feats.includes("디자인")) return false;
            if (special === "biz" && !feats.includes("비즈니스") && !feats.includes("취업")) return false;
            if (special === "jlpt" && !cNames.includes("N1") && !feats.includes("JLPT")) return false;
            if (special === "short" && !cNames.includes("단기")) return false;
        }

        // 기숙사 필터
        if (dorm !== "all") {
            if (dorm === "yes" && !feats.includes("기숙사")) return false;
            if (dorm === "single" && !feats.includes("1인실")) return false;
            if (dorm === "school_owned" && !feats.includes("기숙사")) return false;
        }

        // 장학금 필터
        if (scholarship !== "all") {
            if (!feats.includes("장학금")) return false;
        }

        // EJU 필터
        if (eju !== "all") {
            if (eju === "yes" && !feats.includes("EJU")) return false;
            if (eju === "science" && !feats.includes("이과")) return false;
            if (eju === "art" && !feats.includes("미술")) return false;
        }

        // 회화 필터
        if (convo !== "all") {
            if (convo === "yes" && !feats.includes("회화")) return false;
        }

        // 환경 필터
        if (env !== "all") {
            const isBusy = addr.includes("新宿") || addr.includes("渋谷") || addr.includes("池袋");
            if (env === "quiet" && isBusy) return false;
            if (env === "active" && !isBusy) return false;
        }
        
        return true;
    });

    // 4. 지도 업데이트
    window.isSearchMove = !!(targetUnivLocation && univInput !== "");
    
    renderMarkers(filtered);

    if (targetUnivLocation) {
        map.panTo(targetUnivLocation);
        map.setZoom(14);
    }

    updateFilterUI();
    toggleButtons(true); // 검색 결과가 있으면 Reset 버튼 보이기
}

function resetFilters() {
    // 모든 select 초기화
    document.querySelectorAll(".search-container select").forEach(el => el.value = 'all');
    // 검색창 초기화
    const univInput = document.getElementById("filter-univ");
    if(univInput) univInput.value = "";
    
    window.isSearchMove = false;
    renderMarkers(SCHOOLS_DATA);
    updateFilterUI();
    
    toggleButtons(false); // 초기화 후 Search 버튼 보이기
    
    map.setZoom(5);
    map.setCenter({ lat: 36.2048, lng: 138.2529 });
}