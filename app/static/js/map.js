/* app/static/js/map.js */

let map;
let allSchoolData = []; 
let markers = []; 
let infoWindow;
let LatLngBounds, AdvancedMarkerElement;
let geometry; 

const SVG_SCHOOL = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 58 84" width="32" height="46"><filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/></filter><g filter="url(#shadow)"><path fill="#E67E22" stroke="#FFFFFF" stroke-width="2" d="M29,0C13,0,0,13,0,29c0,16,29,55,29,55s29-39,29-55C58,13,45,0,29,0z"/><circle cx="29" cy="29" r="18" fill="#FFFFFF" opacity="0.2"/><text x="29" y="36" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">JLS</text></g></svg>`;
const SVG_UNIV = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 58 84" width="32" height="46"><filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3"/></filter><g filter="url(#shadow)"><path fill="#3498DB" stroke="#FFFFFF" stroke-width="2" d="M29,0C13,0,0,13,0,29c0,16,29,55,29,55s29-39,29-55C58,13,45,0,29,0z"/><circle cx="29" cy="29" r="18" fill="#FFFFFF" opacity="0.2"/><text x="29" y="36" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">UNI</text></g></svg>`;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const markerLib = await google.maps.importLibrary("marker");
    AdvancedMarkerElement = markerLib.AdvancedMarkerElement;
    
    const coreLib = await google.maps.importLibrary("core");
    LatLngBounds = coreLib.LatLngBounds; 
    
    geometry = await google.maps.importLibrary("geometry");

    map = new Map(document.getElementById("map"), {
        zoom: 5, center: { lat: 35.6895, lng: 139.6917 },
        mapId: "2938bb3f7f034d78a2dbaf56",
        mapTypeControl: false, streetViewControl: false, fullscreenControl: false
    });
    infoWindow = new google.maps.InfoWindow(); 

    if (typeof SCHOOLS_DATA === 'undefined' || !SCHOOLS_DATA || !SCHOOLS_DATA.schools) {
        allSchoolData = [];
    } else {
        allSchoolData = SCHOOLS_DATA.schools;
    }

    bindEvents();
    renderMarkers(allSchoolData);
}

function bindEvents() {
    document.querySelectorAll('.tag-filter-btn').forEach(button => {
        button.addEventListener('click', handleTagFilterClick);
    });

    const univSearchInput = document.getElementById('univ-search-input');
    const univSearchClear = document.getElementById('univ-search-clear');
    
    if (univSearchInput) {
        univSearchInput.addEventListener('input', (e) => {
            handleUnivSearch(e.target.value);
            univSearchClear.style.display = e.target.value ? 'block' : 'none';
        });
    }

    if(univSearchClear) {
        univSearchClear.addEventListener('click', () => {
            univSearchInput.value = '';
            handleUnivSearch('');
            univSearchClear.style.display = 'none';
        });
    }
}

function handleUnivSearch(query) {
    if (!query) {
        document.querySelectorAll('.tag-filter-btn').forEach(btn => btn.disabled = false);
        const activeTag = document.querySelector('.tag-filter-btn.active');
        const filterKey = activeTag ? activeTag.dataset.filterKey : 'all';
        const schools = filterSchoolsByKey(filterKey);
        renderMarkers(schools);
        return;
    }

    document.querySelectorAll('.tag-filter-btn').forEach(btn => btn.disabled = true);

    const lowerQuery = query.toLowerCase();
    
    // [수정] 일본어 이름(name_ja)도 검색 조건에 포함
    const targetUniv = allSchoolData.find(s => 
        s.category === 'university' && 
        ( (s.basic_info.name_ja && s.basic_info.name_ja.toLowerCase().includes(lowerQuery)) || 
          (s.basic_info.name_en && s.basic_info.name_en.toLowerCase().includes(lowerQuery)) )
    );

    if (targetUniv && targetUniv.location) {
        const schoolsToShow = [targetUniv];
        const univPosition = new google.maps.LatLng(targetUniv.location.lat, targetUniv.location.lng);

        allSchoolData.forEach(s => {
            if (s.category !== 'university' && s.location) {
                const schoolPosition = new google.maps.LatLng(s.location.lat, s.location.lng);
                const distance = geometry.spherical.computeDistanceBetween(univPosition, schoolPosition);
                if (distance <= 2000) {
                    schoolsToShow.push(s);
                }
            }
        });
        
        renderMarkers(schoolsToShow);
        map.panTo(univPosition);
        map.setZoom(14);
    } else {
        renderMarkers([]);
    }
}

function handleTagFilterClick(event) {
    const clickedButton = event.currentTarget;
    const filterKey = clickedButton.dataset.filterKey;

    document.querySelectorAll('.tag-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    clickedButton.classList.add('active');

    const filteredSchools = filterSchoolsByKey(filterKey);
    renderMarkers(filteredSchools);
}

function filterSchoolsByKey(key) {
    if (key === 'all') {
        return allSchoolData;
    }
    const ACADEMIC_KEYWORDS = ["eju", "university", "academic", "進学", "大学"];
    const BIZ_KEYWORDS = ["business", "job", "취업", "ビジネス"];
    const CULTURE_KEYWORDS = ["conversation", "culture", "short-term", "회화", "短期", "문화"];
    
    return allSchoolData.filter(s => {
        if (s.category === 'university') return false; 
        
        const features = (s.features || []).join(" ").toLowerCase();
        
        switch(key) {
            case 'academic': return ACADEMIC_KEYWORDS.some(kw => features.includes(kw));
            case 'business': return BIZ_KEYWORDS.some(kw => features.includes(kw));
            case 'culture': return CULTURE_KEYWORDS.some(kw => features.includes(kw));
            case 'affordable':
                const cost = s.tuition?.yearly_tuition || s.tuition;
                return typeof cost === 'number' && cost < 800000;
            case 'international':
                const demo = s.stats?.student_demographics || {};
                if (!demo || Object.keys(demo).length === 0) return false;
                const total = Object.values(demo).reduce((sum, val) => sum + (val || 0), 0);
                if (total === 0) return false;
                const topRatio = Math.max(...Object.values(demo).map(v => v || 0)) / total;
                return topRatio <= 0.6;
            default: return true;
        }
    });
}

function renderMarkers(data) {
    markers.forEach(m => m.map = null);
    markers = [];
    if (!data || !map || !LatLngBounds || !AdvancedMarkerElement) { return; }
    
    const bounds = new LatLngBounds();
    const parser = new DOMParser();
    
    data.forEach(item => {
        if (!item.location || !item.location.lat) return;
        const position = { lat: item.location.lat, lng: item.location.lng };
        const isUniv = (item.category === 'university');
        const svgString = isUniv ? SVG_UNIV : SVG_SCHOOL;
        const pinContent = parser.parseFromString(svgString, 'image/svg+xml').documentElement;
        const marker = new AdvancedMarkerElement({ map, position, title: item.basic_info.name_ja, content: pinContent, zIndex: isUniv ? 9999 : 1 });
        marker.addListener("click", () => openInfoWindow(item, marker));
        markers.push(marker);
        bounds.extend(position);
    });
    
    if (markers.length > 0) {
        if (markers.length === 1) {
            map.setCenter(bounds.getCenter());
            map.setZoom(14);
        } else {
            map.fitBounds(bounds);
        }
    }
}

function openInfoWindow(school, marker) {
    const labelColor = school.category === 'university' ? '#3498DB' : '#E67E22'; 
    const labelText = school.category === 'university' ? 'UNIVERSITY' : 'LANGUAGE SCHOOL';
    const contentString = `
        <div class="info-window-card">
            <div class="iw-header" style="border-left: 5px solid ${labelColor}; padding-left:15px; margin-bottom:10px;">
                <span style="font-size:0.75rem; font-weight:bold; color:${labelColor};">${labelText}</span>
                <a href="${school.link}" class="iw-title">${school.basic_info.name_ja}</a>
            </div>
            <div class="iw-body">
                <div class="iw-row"><i class="fas fa-map-marker-alt iw-icon"></i><span>${school.basic_info.address || 'N/A'}</span></div>
                ${school.basic_info.capacity ? `<div class="iw-row"><i class="fas fa-users iw-icon"></i><span>Capacity: ${school.basic_info.capacity}</span></div>` : ''}
                <a href="${school.link}" class="iw-btn" style="background-color: ${labelColor}; color: white;">View Details</a>
            </div>
        </div>`;
    infoWindow.setContent(contentString);
    infoWindow.open({ anchor: marker, map });
}