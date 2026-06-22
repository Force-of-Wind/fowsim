/*
 * Read-only venue map on the tournament detail page. Renders the stored
 * coordinates with a marker - no geocoding happens here, so public page views
 * never call Nominatim. Only loaded when the tournament has map coordinates.
 */
$(document).ready(function () {
    const el = document.getElementById('tournament-map');
    if (!el || typeof L === 'undefined') {
        return;
    }

    const lat = parseFloat(el.dataset.lat);
    const lng = parseFloat(el.dataset.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        return;
    }

    // Resolve Leaflet's default marker icons against the CDN.
    const CDN = 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/images/';
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: CDN + 'marker-icon-2x.png',
        iconUrl: CDN + 'marker-icon.png',
        shadowUrl: CDN + 'marker-shadow.png',
    });

    const latlng = [lat, lng];
    const map = L.map('tournament-map', { scrollWheelZoom: false }).setView(latlng, 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    const marker = L.marker(latlng).addTo(map);
    const label = (el.dataset.label || '').trim();
    if (label) {
        // Leaflet treats a string popup as raw HTML (innerHTML), and the label
        // comes from the staff-entered location, so escape it to avoid XSS.
        marker.bindPopup($('<div>').text(label).html());
    }
});
