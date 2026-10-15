/*
 * In-person venue picker for the tournament create/edit forms.
 *
 * Uses Leaflet + OpenStreetMap tiles (no API key) and the leaflet-geosearch
 * Nominatim provider for address lookup. Geocoding only happens here, while a
 * staff member is actively editing - the public detail page just renders the
 * stored coordinates, so we never hit Nominatim on normal page views.
 *
 * The map only exists when the form rendered the location_lat / location_lng
 * hidden inputs (i.e. a map-enabled tournament). Legacy tournaments lack those
 * inputs and are left untouched.
 */
$(document).ready(function () {
    const latInput = document.getElementById('location_lat');
    const lngInput = document.getElementById('location_lng');
    const wrapper = document.getElementById('location-map-wrapper');
    const onlineToggle = document.getElementById('is_online');
    const locationField = document.getElementById('location');

    if (!latInput || !lngInput || !wrapper || typeof L === 'undefined') {
        return;
    }

    // Leaflet's default marker icons are resolved relative to the bundled JS,
    // which breaks when served from a CDN. Point them at the CDN images.
    const CDN = 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/images/';
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: CDN + 'marker-icon-2x.png',
        iconUrl: CDN + 'marker-icon.png',
        shadowUrl: CDN + 'marker-shadow.png',
    });

    const DEFAULT_CENTER = [50.0, 10.0]; // Central Europe overview
    const DEFAULT_ZOOM = 4;
    const PIN_ZOOM = 16;

    let map = null;
    let marker = null;
    // Holds the last known pin while the map is hidden for an online event, so
    // toggling back to in-person can restore it instead of losing the venue.
    let savedLatLng = null;

    function readStored() {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
            return L.latLng(lat, lng);
        }
        return null;
    }

    function writeCoords(latlng) {
        latInput.value = latlng.lat.toFixed(6);
        lngInput.value = latlng.lng.toFixed(6);
    }

    function clearCoords() {
        // Remember the current pin before clearing so switching back to
        // in-person can put it back rather than silently dropping it.
        savedLatLng = readStored() || savedLatLng;
        latInput.value = '';
        lngInput.value = '';
    }

    function placeMarker(latlng) {
        if (marker) {
            marker.setLatLng(latlng);
        } else {
            marker = L.marker(latlng, { draggable: true }).addTo(map);
            marker.on('dragend', function () {
                writeCoords(marker.getLatLng());
            });
        }
        writeCoords(latlng);
    }

    function initMap() {
        const stored = readStored();

        map = L.map('location-map').setView(stored || DEFAULT_CENTER, stored ? PIN_ZOOM : DEFAULT_ZOOM);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        if (stored) {
            placeMarker(stored);
        }

        // Address search box (Nominatim via leaflet-geosearch).
        if (typeof GeoSearch !== 'undefined') {
            const search = new GeoSearch.GeoSearchControl({
                provider: new GeoSearch.OpenStreetMapProvider(),
                style: 'bar',
                showMarker: false,
                autoClose: true,
                keepResult: true,
                searchLabel: 'Search for the venue address',
            });
            map.addControl(search);

            map.on('geosearch/showlocation', function (result) {
                const latlng = L.latLng(result.location.y, result.location.x);
                map.setView(latlng, PIN_ZOOM);
                placeMarker(latlng);
                // Pre-fill the human-readable location only if left blank.
                if (locationField && !locationField.value.trim()) {
                    locationField.value = result.location.label;
                }
            });
        }

        // Click anywhere to drop / move the pin.
        map.on('click', function (e) {
            placeMarker(e.latlng);
        });
    }

    function showMap() {
        wrapper.hidden = false;
        if (!map) {
            initMap();
        }
        // Restore a pin that was cleared when the event was toggled online.
        if (!readStored() && savedLatLng) {
            map.setView(savedLatLng, PIN_ZOOM);
            placeMarker(savedLatLng);
        }
        // Leaflet miscalculates size when initialised inside a hidden element.
        window.setTimeout(function () {
            if (map) {
                map.invalidateSize();
            }
        }, 50);
    }

    function hideMap() {
        wrapper.hidden = true;
        // Online events have no physical venue - drop any stored pin.
        clearCoords();
    }

    function sync() {
        if (onlineToggle && onlineToggle.checked) {
            hideMap();
        } else {
            showMap();
        }
    }

    if (onlineToggle) {
        $(onlineToggle).on('change', sync);
    }
    sync();
});
