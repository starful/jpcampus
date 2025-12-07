/* app/static/js/map.js */

let map;
let markers = [];
let markerCluster;
let infoWindow;

function initMap() {
    console.log("🏫 로드된 학교 데이터 개수:", SCHOOLS_DATA.length);
    
    const japanCenter = { lat: 38.0, lng: 137.0 }; 
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: japanCenter,
        zoom: 5,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        styles: [{ "featureType": "poi", "elementType": "labels", "stylers": [{ "visibility": "off" }] }]
    });

    infoWindow = new google.maps.InfoWindow();

    renderMarkers(SCHOOLS_DATA);
    
    // Select 박스 이벤트
    document.querySelectorAll('.search-container select').forEach(select => {
        select.addEventListener('change', () => {
            updateFilterUI();
            applyFilters();
        });
    });

    // 검색창(Input) 이벤트
    const univInput = document.getElementById("filter-univ");
    if (univInput) {
        univInput.addEventListener('input', () => {
             updateFilterUI(); // 입력할 때마다 색상 변경 체크
             applyFilters(); 
        });
    }
}

// 필터 UI 업데이트 (녹색 활성화)
function updateFilterUI() {
    // 1. Select 박스 처리
    document.querySelectorAll('.search-container select').forEach(sel => {
        if (sel.value !== 'all') {
            sel.classList.add('active-filter');
        } else {
            sel.classList.remove('active-filter');
        }
    });

    // 2. Input(검색창) 처리 [수정됨]
    const input = document.getElementById("filter-univ");
    if (input) {
        if (input.value.trim() !== "") {
            input.classList.add('active-filter');
        } else {
            input.classList.remove('active-filter');
        }
    }
}

function renderMarkers(data) {
    if (markerCluster) {
        markerCluster.clearMarkers();
    }
    markers = [];

    const bounds = new google.maps.LatLngBounds();
    let hasValidLocation = false;

    data.forEach(school => {
        if (!school.location || !school.location.lat) return;

        hasValidLocation = true;
        const position = { lat: school.location.lat, lng: school.location.lng };

        let iconColor = "#EA4335"; 
        const features = school.features || [];
        const fees = school.courses ? school.courses.map(c => c.total_fees || 9999999) : [];
        const minFee = Math.min(...fees);
        const career = school.career_path || { grad_school: 0, university: 0 };

        if (features.some(f => f.includes("미술") || f.includes("디자인"))) {
            iconColor = "#9B59B6"; 
        } else if (minFee < 820000) {
            iconColor = "#2ECC71"; 
        } else if ((career.grad_school + career.university) > 50) {
            iconColor = "#3498DB"; 
        }

        const marker = new google.maps.Marker({
            position: position,
            title: school.basic_info.name_ja,
            icon: {
                path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
                fillColor: iconColor,
                fillOpacity: 1,
                strokeWeight: 1,
                strokeColor: "#FFFFFF",
                scale: 1.5,
                anchor: new google.maps.Point(12, 22),
                labelOrigin: new google.maps.Point(12, 9)
            }
        });

        marker.addListener("click", () => {
            // 태그 생성 (최대 3개)
            const featureTags = features.slice(0, 3).map(f => `<span class="iw-tag">${f}</span>`).join('');
            
            // [수정] 카드 디자인 HTML
            const content = `
                <div class="info-window-card">
                    <div class="iw-header">
                        <a href="/school/${school.id}" class="iw-title">${school.basic_info.name_ja}</a>
                        <i class="fas fa-chevron-right" style="color:white; font-size:0.8rem;"></i>
                    </div>
                    <div class="iw-body">
                        <div class="iw-row">
                            <i class="fas fa-map-marker-alt iw-icon"></i>
                            <div>${school.basic_info.address}</div>
                        </div>
                        <div class="iw-row">
                            <i class="fas fa-users iw-icon"></i>
                            <div>정원 ${school.basic_info.capacity}명</div>
                        </div>
                         <div class="iw-row">
                            <i class="fas fa-yen-sign iw-icon"></i>
                            <div>최저 ${minFee !== 9999999 ? (minFee/10000).toLocaleString() + '만엔' : '-'}</div>
                        </div>
                        <div class="iw-tags">${featureTags}</div>
                        <a href="/school/${school.id}" class="iw-btn">상세 정보 보기</a>
                    </div>
                </div>
            `;
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
        });

        markers.push(marker);
        bounds.extend(position);
    });

    markerCluster = new markerClusterer.MarkerClusterer({ markers, map });

    const countEl = document.getElementById("result-count");
    if (countEl) countEl.innerText = markers.length;

    if (markers.length > 0 && hasValidLocation) {
        map.fitBounds(bounds);
    } else {
        map.setCenter({ lat: 35.6895, lng: 139.6917 });
        map.setZoom(10);
    }
}

function applyFilters() {
    const region = document.getElementById("filter-region")?.value || "all";
    const univInput = document.getElementById("filter-univ")?.value.trim() || "";
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

    const filtered = SCHOOLS_DATA.filter(s => {
        const feats = (s.features || []).join(" ");
        const courseNames = (s.courses || []).map(c => c.course_name).join(" ");
        const addr = s.basic_info.address || "";
        const capacity = s.basic_info.capacity || 0;
        const majorUnivs = (s.career_path && s.career_path.major_universities) ? s.career_path.major_universities : [];
        const univString = majorUnivs.join(" ");

        if (region !== "all" && !addr.includes(region)) return false;

        // 대학 검색 (일본어)
        if (univInput !== "") {
            if (majorUnivs.length === 0 || !univString.includes(univInput)) return false;
        }

        if (price !== "all") {
            const fees = (s.courses || []).map(c => c.total_fees).filter(f => typeof f === 'number');
            if (fees.length === 0) return false;
            const minFee = Math.min(...fees);
            if (minFee > parseInt(price) * 10000) return false;
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
            if (scale === "large" && capacity < 400) return false;
            if (scale === "medium" && (capacity < 150 || capacity >= 400)) return false;
            if (scale === "small" && capacity >= 150) return false;
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
            if (special === "jlpt" && !courseNames.includes("N1") && !feats.includes("JLPT")) return false;
            if (special === "short" && !courseNames.includes("단기")) return false;
        }

        if (dorm !== "all") {
            if (!feats.includes("기숙사")) return false;
            if (dorm === "single" && !feats.includes("1인실")) return false;
        }

        if (scholarship === "yes" && !feats.includes("장학금")) return false;

        if (eju !== "all") {
            if (!feats.includes("EJU") && !courseNames.includes("EJU")) return false;
            if (eju === "science" && !feats.includes("이과") && !feats.includes("수학")) return false;
        }

        if (convo === "yes" && !feats.includes("회화") && !courseNames.includes("회화")) return false;

        if (env !== "all") {
            const isBusy = addr.includes("新宿") || addr.includes("渋谷") || addr.includes("池袋");
            if (env === "quiet" && isBusy) return false;
            if (env === "active" && !isBusy) return false;
        }

        return true;
    });

    renderMarkers(filtered);
    
    // UI 업데이트 (필터 상태 반영)
    updateFilterUI();

    const resetBtn = document.getElementById("reset-btn");
    const searchBtn = document.getElementById("search-btn");
    if(resetBtn) resetBtn.style.display = "inline-block";
    if(searchBtn) searchBtn.style.display = "none";
}

function resetFilters() {
    document.querySelectorAll(".search-container select").forEach(el => el.value = 'all');
    const univInput = document.getElementById("filter-univ");
    if(univInput) univInput.value = "";
    
    renderMarkers(SCHOOLS_DATA);
    updateFilterUI();
    
    const resetBtn = document.getElementById("reset-btn");
    const searchBtn = document.getElementById("search-btn");
    if(resetBtn) resetBtn.style.display = "none";
    if(searchBtn) searchBtn.style.display = "inline-block";
}