/* app/static/js/map.js */

let map;
let markers = [];
let markerCluster;
let infoWindow;

// 초기 지도 설정 (일본 전체가 보이도록 대략적인 중심 설정)
function initMap() {
    const japanCenter = { lat: 38.0, lng: 137.0 }; // 일본 중앙
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: japanCenter,
        zoom: 5, // 초기 줌 레벨을 넓게 설정
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        styles: [
            {
                "featureType": "poi",
                "elementType": "labels",
                "stylers": [{ "visibility": "off" }] // 지도 잡다한 라벨 숨김
            }
        ]
    });

    infoWindow = new google.maps.InfoWindow();

    // 초기 마커 렌더링 (전체 데이터)
    renderMarkers(SCHOOLS_DATA);
}

// 마커 생성 및 지도 범위 재설정 함수
function renderMarkers(data) {
    // 1. 기존 마커 및 클러스터 제거
    if (markerCluster) {
        markerCluster.clearMarkers();
    }
    markers = [];

    // 2. 지도 범위(Bounds) 객체 생성
    const bounds = new google.maps.LatLngBounds();
    let hasValidLocation = false;

    // 3. 데이터 루프 돌면서 마커 생성
    data.forEach(school => {
        if (!school.location || !school.location.lat) return;

        hasValidLocation = true;
        const position = { lat: school.location.lat, lng: school.location.lng };

        // 색상 결정 로직
        let iconColor = "#EA4335"; // 기본: 빨강
        if (school.features && school.features.some(f => f.includes("미술") || f.includes("디자인"))) {
            iconColor = "#9B59B6"; // 미술: 보라
        } else if (school.courses && school.courses.some(c => c.total_fees < 820000)) {
            iconColor = "#2ECC71"; // 저렴: 초록
        } else if (school.career_path && (school.career_path.grad_school + school.career_path.university > 50)) {
            iconColor = "#3498DB"; // 진학: 파랑
        }

        // 마커 생성 (SVG 아이콘 사용)
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

        // 클릭 이벤트 (인포윈도우)
        marker.addListener("click", () => {
            const content = `
                <div class="info-window-card">
                    <a href="/school/${school.id}" class="info-link">${school.basic_info.name_ja} <i class="fas fa-chevron-right"></i></a>
                    <div class="info-meta">
                        <div class="meta-row"><i class="fas fa-map-marker-alt meta-icon"></i> ${school.basic_info.address}</div>
                        <div class="meta-row"><i class="fas fa-users meta-icon"></i> 정원 ${school.basic_info.capacity}명</div>
                    </div>
                    <div class="info-tags">
                        ${school.features ? school.features.slice(0, 2).map(f => `<span class="tag" style="background:#eee;">${f}</span>`).join('') : ''}
                    </div>
                </div>
            `;
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
        });

        markers.push(marker);
        
        // [중요] 마커 위치를 지도 범위에 추가
        bounds.extend(position);
    });

    // 4. 마커 클러스터링 적용
    markerCluster = new markerClusterer.MarkerClusterer({ markers, map });

    // 5. 결과 개수 업데이트
    const countEl = document.getElementById("result-count");
    if (countEl) countEl.innerText = markers.length;

    // 6. [핵심] 지도 범위를 마커들에 맞게 자동 조정 (fitBounds)
    if (markers.length > 0 && hasValidLocation) {
        map.fitBounds(bounds);
        
        // (선택사항) 결과가 1개나 너무 적어서 줌이 과하게 땡겨지는 경우 방지하려면 아래 로직 추가 가능하지만,
        // 구글맵 기본 fitBounds가 꽤 똑똑해서 보통은 그냥 둡니다.
    } else {
        // 결과가 없으면 일본 전체 뷰로 리셋
        map.setCenter({ lat: 38.0, lng: 137.0 });
        map.setZoom(5);
    }
}

// 필터 적용 함수
function applyFilters() {
    const region = document.getElementById("filter-region").value;
    const price = document.getElementById("filter-price").value;
    const nation = document.getElementById("filter-nation").value;
    const special = document.getElementById("filter-special").value;
    
    // 추가된 필터들
    const scale = document.getElementById("filter-scale").value;
    const career = document.getElementById("filter-career").value;
    const dorm = document.getElementById("filter-dorm").value;
    const scholarship = document.getElementById("filter-scholarship").value;
    const eju = document.getElementById("filter-eju").value;
    const convo = document.getElementById("filter-convo").value;
    const env = document.getElementById("filter-env").value;

    const filtered = SCHOOLS_DATA.filter(s => {
        // 1. 지역 필터 (확장됨)
        if (region !== "all") {
            const addr = s.basic_info.address || "";
            // 도쿄/치바/사이타마 등 현 이름이나 도시 이름이 포함되는지 확인
            if (!addr.includes(region)) return false;
        }

        // 2. 학비 필터
        if (price !== "all") {
            const fees = s.courses.map(c => c.total_fees).filter(f => typeof f === 'number');
            if (fees.length === 0) return false;
            const minFee = Math.min(...fees);
            if (minFee > parseInt(price) * 10000) return false;
        }

        // 3. 국적 필터
        if (nation !== "all") {
            const demo = s.student_demographics;
            const total = demo.total || 0;
            if (total === 0) return false;

            const krRatio = demo.korea / total;
            const westRatio = (demo.usa || 0) / total; // USA 등을 서구권 대표로 임시 활용
            const cnRatio = (demo.china || 0) / total;
            const vnRatio = (demo.vietnam || 0) / total;

            if (nation === "global" && westRatio < 0.1) return false; // 서구권 10% 이상
            if (nation === "korea_low" && krRatio > 0.3) return false; // 한국인 30% 이하
            if (nation === "china_high" && cnRatio < 0.5) return false;
            if (nation === "vietnam_high" && vnRatio < 0.3) return false;
        }

        // 4. 특화 필터
        if (special !== "all") {
            const feats = (s.features || []).join(" ");
            const courses = s.courses.map(c => c.course_name).join(" ");
            
            if (special === "art" && !feats.includes("미술") && !feats.includes("디자인")) return false;
            if (special === "biz" && !feats.includes("비즈니스") && !feats.includes("취업")) return false;
            if (special === "jlpt" && !courses.includes("N1") && !feats.includes("JLPT")) return false;
            if (special === "short" && !courses.includes("단기")) return false;
        }

        return true;
    });

    renderMarkers(filtered);
    
    // [UI] 초기화 버튼 보이기
    document.getElementById("reset-btn").style.display = "inline-block";
    document.getElementById("search-btn").style.display = "none";
}

// 필터 초기화 함수
function resetFilters() {
    // 모든 select를 'all'로 되돌림
    document.querySelectorAll(".search-container select").forEach(el => el.value = 'all');
    
    renderMarkers(SCHOOLS_DATA);
    
    // 버튼 상태 복구
    document.getElementById("reset-btn").style.display = "none";
    document.getElementById("search-btn").style.display = "inline-block";
}