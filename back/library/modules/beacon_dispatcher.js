/**
 * sdk/modules/beacon_dispatcher.js
 * Despacho en lote no bloqueante vía sendBeacon / fetch keepalive.
 * Gobernanza: Límite estricto < 150 líneas.
 */
export function createBeaconDispatcher(apiEndpoint, siteKey) {
    const buffer = [];

    function push(eventType, eventData) {
        buffer.push({
            event_type: eventType,
            page_url: window.location.href,
            event_data: eventData || {}
        });
    }

    function flush() {
        if (buffer.length === 0) return;
        const payload = JSON.stringify({
            site_key: siteKey,
            events: buffer.splice(0, buffer.length)
        });

        if (navigator.sendBeacon) {
            const blob = new Blob([payload], { type: 'text/plain' });
            navigator.sendBeacon(apiEndpoint, blob);
        } else {
            fetch(apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: payload,
                keepalive: true
            });
        }
    }

    window.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') flush();
    });
    window.addEventListener('pagehide', flush);
    window.addEventListener('beforeunload', flush);

    return { push: push, flush: flush, getBufferSize: function() { return buffer.length; } };
}
