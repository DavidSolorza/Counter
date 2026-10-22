/**
 * WolfAnalytics Client SDK (v1.1.0 - Flexible JSON Payload)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";

    const scriptTag = document.currentScript || document.querySelector('script[data-site-key]');
    if (!scriptTag) return;

    const siteKey = scriptTag.getAttribute('data-site-key');
    if (!siteKey) {
        console.error("WolfAnalytics: Falta la Site Key. El SDK está bloqueado.");
        return;
    }

    const API_BASE = scriptTag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';

    // 1. EL HANDSHAKE: Validar la llave contra la API antes de activar el SDK
    fetch(API_BASE + '/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_key: siteKey })
    })
    .then(function(res) {
        return res.json().then(function(data) {
            return { ok: res.ok, status: res.status, data: data };
        });
    })
    .then(function(result) {
        if (!result.ok || !result.data.valid) {
            console.warn("WolfAnalytics: SDK Bloqueado ->", result.data.error || "Licencia inactiva.");
            return; // BLOQUEO TOTAL
        }

        console.info("WolfAnalytics: Licencia activa. Iniciando recolección para:", result.data.domain);
        initializeTracker(siteKey, API_BASE);
    })
    .catch(function(err) {
        console.error("WolfAnalytics: No se pudo conectar con el servidor de licencias.", err);
    });

    // 2. MOTOR DE RECOLECCIÓN FLEXIBLE
    function initializeTracker(key, apiBase) {
        const eventsBuffer = [];

        function pushEvent(eventType, eventData) {
            eventsBuffer.push({
                event_type: eventType,
                page_url: window.location.href,
                event_data: eventData || {}
            });
        }

        // Registrar visita inicial (Pageview)
        pushEvent('pageview', {
            title: document.title || 'Page',
            referrer: document.referrer || null,
            screen: window.innerWidth + 'x' + window.innerHeight
        });

        // Interceptar clics en el DOM
        document.addEventListener('click', function(e) {
            const el = e.target;
            const identifier = el.tagName + (el.id ? '#' + el.id : '') +
                (el.className ? '.' + String(el.className).split(' ')[0] : '');

            pushEvent('click', {
                element: identifier,
                text: (el.innerText || '').slice(0, 50).trim(),
                dataset: Object.assign({}, el.dataset)
            });
        }, true);

        // Envío seguro antes de abandonar la página (sendBeacon / fetch keepalive)
        function flushEvents() {
            if (eventsBuffer.length === 0) return;
            const payload = JSON.stringify({ site_key: key, events: eventsBuffer });
            const endpoint = apiBase + '/telemetry';

            if (navigator.sendBeacon) {
                const blob = new Blob([payload], { type: 'text/plain' });
                navigator.sendBeacon(endpoint, blob);
            } else {
                fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: payload,
                    keepalive: true
                });
            }
        }

        window.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') flushEvents();
        });
        window.addEventListener('pagehide', flushEvents);
        window.addEventListener('beforeunload', flushEvents);

        // API pública para enviar eventos personalizados con JSON enriquecido
        window.WolfAnalytics = {
            track: function(eventType, customData) {
                pushEvent(eventType, customData);
            },
            flush: flushEvents
        };

        // Actualizar dinámicamente el badge si existe
        fetch(apiBase + '/stats/' + encodeURIComponent(key))
            .then(function(res) { return res.json(); })
            .then(function(data) {
                const badge = document.getElementById('wc-number');
                if (badge && typeof data.total_events === 'number') {
                    badge.textContent = data.total_events;
                }
            })
            .catch(function() {});
    }
})();
