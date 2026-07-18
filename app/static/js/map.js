/* app/static/js/map.js — schools + student housing markers */

let map;
let markers = [];
let infoWindow;
let markerById = {};
let mapReady = false;

const STAY_TYPE_LABELS = {
    guesthouse: "Guesthouse",
    share_house: "Share House",
    monthly_mansion: "Monthly Mansion",
};

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    window.AdvancedMarkerElement = AdvancedMarkerElement;

    map = new Map(document.getElementById("map"), {
        zoom: 11,
        center: { lat: 35.6762, lng: 139.6503 },
        mapId: "2938bb3f7f034d78c237cb68",
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        zoomControlOptions: { position: google.maps.ControlPosition.TOP_RIGHT },
    });

    infoWindow = new google.maps.InfoWindow({ minWidth: 280, disableAutoPan: true });
    mapReady = true;

    bindCardInteractions();

    const schools = window.JPCampusFilters?.getCurrentFilteredSchools?.() || [];
    const stays = window.JPCampusFilters?.getCurrentFilteredStays?.() || [];
    renderMarkers(schools, stays);
}

window.initMap = initMap;

document.addEventListener("jpcampus:filter", (event) => {
    renderMarkers(event.detail?.schools || [], event.detail?.stays || []);
});

function bindCardInteractions() {
    document.querySelectorAll(".school-card[data-school-id], .university-card[data-school-id]").forEach((card) => {
        const schoolId = card.dataset.schoolId;
        card.addEventListener("mouseenter", () => highlightMarkerById(`school:${schoolId}`, true));
        card.addEventListener("mouseleave", () => highlightMarkerById(`school:${schoolId}`, false));
    });
    document.querySelectorAll(".stay-card[data-stay-id]").forEach((card) => {
        const stayId = card.dataset.stayId;
        card.addEventListener("mouseenter", () => highlightMarkerById(`stay:${stayId}`, true));
        card.addEventListener("mouseleave", () => highlightMarkerById(`stay:${stayId}`, false));
    });
}

function renderMarkers(schools, stays) {
    markers.forEach((m) => { m.map = null; });
    markers = [];
    markerById = {};

    if (!mapReady || !map || !window.AdvancedMarkerElement) return;

    const bounds = new google.maps.LatLngBounds();
    let count = 0;

    (schools || []).forEach((item) => {
        const marker = createSchoolMarker(item, bounds);
        if (marker) count += 1;
    });

    (stays || []).forEach((item) => {
        const marker = createStayMarker(item, bounds);
        if (marker) count += 1;
    });

    if (count === 0) return;

    if (count === 1) {
        map.setCenter(bounds.getCenter());
        map.setZoom(14);
        return;
    }

    map.fitBounds(bounds, 80);
    const zoom = map.getZoom();
    if (zoom > 15) map.setZoom(15);
    if (zoom < 5) map.setZoom(5);
}

function createSchoolMarker(item, bounds) {
    if (!item.location || item.location.lat == null) return null;

    // Always use type icons (not photo pins) so university / school / stay stay distinct.
    const isUniv = item.category === "university";
    const markerEl = document.createElement("div");
    if (isUniv) {
        markerEl.className = "map-marker marker-univ";
        markerEl.innerHTML = '<i class="fa-solid fa-building-columns"></i>';
    } else {
        markerEl.className = "map-marker marker-school";
        markerEl.innerHTML = '<i class="fa-solid fa-graduation-cap"></i>';
    }

    const marker = new window.AdvancedMarkerElement({
        map,
        position: item.location,
        title: item.basic_info?.name_en || item.basic_info?.name_ja,
        content: markerEl,
        zIndex: isUniv ? 100 : 20,
    });

    marker.addListener("click", () => openSchoolInfoWindow(item, marker));
    markers.push(marker);
    const key = `school:${item.id}`;
    markerById[key] = marker;
    bounds.extend(item.location);
    return marker;
}

function createStayMarker(item, bounds) {
    if (!item.location || item.location.lat == null) return null;

    const markerEl = document.createElement("div");
    markerEl.className = `map-marker marker-stay marker-stay-${item.stay_type || "guesthouse"}`;
    markerEl.innerHTML = '<i class="fa-solid fa-house-chimney"></i>';

    const marker = new window.AdvancedMarkerElement({
        map,
        position: item.location,
        title: item.basic_info?.name_en || item.basic_info?.name_ja,
        content: markerEl,
        zIndex: 60,
    });

    marker.addListener("click", () => openStayInfoWindow(item, marker));
    markers.push(marker);
    const key = `stay:${item.id}`;
    markerById[key] = marker;
    bounds.extend(item.location);
    return marker;
}

function getCompareLabels() {
    const cfg = window.JPCAMPUS_COMPARE || {};
    return {
        default: cfg.labelDefault || "+ Compare",
        selected: cfg.labelSelected || "✓ Comparing",
    };
}

function getCompareButtonLabel(id) {
    const labels = getCompareLabels();
    const ids = window.JPCampusCompare?.getCompareItems?.() || [];
    return ids.includes(id) ? labels.selected : labels.default;
}

function openSchoolInfoWindow(school, marker) {
    const isUniv = school.category === "university";
    const labelColor = isUniv ? "var(--accent)" : "var(--primary)";
    const labelText = isUniv ? "University" : "Language School";
    const compareLabels = getCompareLabels();
    const compareLabel = getCompareButtonLabel(school.id);

    if (infoWindow) infoWindow.close();

    infoWindow.setContent(`
        <div class="info-window-content">
            <div class="iw-header">
                <span class="iw-badge" style="background-color: ${labelColor};">${labelText}</span>
                <h5 class="iw-title">${school.basic_info.name_en || school.basic_info.name_ja}</h5>
                <p class="iw-address">${school.basic_info.address || "Address not available"}</p>
            </div>
            <div class="iw-actions">
                <button type="button" class="compare-toggle-btn iw-compare-btn" data-compare-id="${school.id}" data-label-default="${compareLabels.default}" data-label-selected="${compareLabels.selected}" aria-pressed="false">${compareLabel}</button>
                <a href="${school.link}" class="iw-details-btn">View Details →</a>
            </div>
        </div>`);

    infoWindow.open({ anchor: marker, map });
    highlightCardBySchoolId(school.id);
    highlightMarkerById(`school:${school.id}`, true);
    setTimeout(() => highlightMarkerById(`school:${school.id}`, false), 1400);
    trackEvent("marker_click", `school:${school.id}`);
}

function openStayInfoWindow(stay, marker) {
    const typeLabel = STAY_TYPE_LABELS[stay.stay_type] || "Housing";
    const rentMin = stay.rent?.min ? `¥${Number(stay.rent.min).toLocaleString()}/mo` : "";

    if (infoWindow) infoWindow.close();

    infoWindow.setContent(`
        <div class="info-window-content">
            <div class="iw-header">
                <span class="iw-badge" style="background-color:#c026d3;">${typeLabel}</span>
                <h5 class="iw-title">${stay.basic_info.name_en || stay.basic_info.name_ja}</h5>
                <p class="iw-address">${stay.basic_info.address || ""}</p>
                ${rentMin ? `<p class="iw-rent">${rentMin}</p>` : ""}
            </div>
            <div class="iw-actions">
                <a href="${stay.link}" class="iw-details-btn">View Details →</a>
            </div>
        </div>`);

    infoWindow.open({ anchor: marker, map });
    highlightCardByStayId(stay.id);
    highlightMarkerById(`stay:${stay.id}`, true);
    setTimeout(() => highlightMarkerById(`stay:${stay.id}`, false), 1400);
    trackEvent("marker_click", `stay:${stay.id}`);
}

function highlightCardBySchoolId(schoolId) {
    if (!schoolId) return;
    const card = document.querySelector(`.school-card[data-school-id="${schoolId}"], .university-card[data-school-id="${schoolId}"]`);
    if (!card) return;
    card.classList.add("is-highlighted");
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(() => card.classList.remove("is-highlighted"), 1600);
}

function highlightCardByStayId(stayId) {
    if (!stayId) return;
    const card = document.querySelector(`.stay-card[data-stay-id="${stayId}"]`);
    if (!card) return;
    card.classList.add("is-highlighted");
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(() => card.classList.remove("is-highlighted"), 1600);
}

function highlightMarkerById(markerKey, isActive) {
    const marker = markerById[markerKey];
    if (!marker || !marker.content) return;
    marker.content.classList.toggle("map-marker-active", !!isActive);
}

function trackEvent(action, label) {
    if (typeof window.gtag === "function") {
        window.gtag("event", action, {
            event_category: "ux_interaction",
            event_label: label || "",
        });
    }
}
