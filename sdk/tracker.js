/**
 * Counter Analytics Enterprise SDK (v2.2.0 - PII Sanitizer & Total Failsafe)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";
    try {
        const tag = document.currentScript || document.querySelector('script[data-site-key]');
        if (!tag) return;
        const key = tag.getAttribute('data-site-key');
        if (!key) return;

        const isDebug = tag.getAttribute('data-debug') === 'true';
        const API_BASE = tag.getAttribute('data-api-base') || 'http://127.0.0.1:5000/api/v1';

        function log(msg, d) {
            if (isDebug) console.log("%c[Counter] " + msg, "color: #22c55e; font-weight: bold;", d || "");
        }

        // Sanitización de Información Personalmente Identificable (PII)
        function isSensitive(el) {
            if (!el) return false;
            const type = (el.type || '').toLowerCase();
            const tagN = (el.tagName || '').toLowerCase();
            const name = (el.name || el.id || '').toLowerCase();
            if (type === 'password' || el.hasAttribute('data-private')) return true;
            return /password|passwd|card|cc-num|cvv|cvc|token|ssn|secret/i.test(name);
        }

        fetch(API_BASE + '/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ site_key: key })
        })
        .then(r => r.json())
        .then(function(res) {
            if (!res.valid) return;
            log("Desbloqueado para dominio:", res.domain);
            boot(key, API_BASE);
        })
        .catch(() => {});

        function boot(siteKey, apiBase) {
            const buffer = [];
            let startTime = Date.now(), dwellMs = 0, isVis = document.visibilityState === 'visible';
            let timer = null;

            function emit(t, d, imm) {
                try {
                    buffer.push({ event_type: t, page_url: window.location.href, event_data: d || {} });
                    log("Capturado (" + t + "):", d);
                    if (imm) flush(); else { clearTimeout(timer); timer = setTimeout(flush, 1200); }
                } catch(e) {}
            }

            function flush() {
                try {
                    if (buffer.length === 0) return;
                    const batch = buffer.splice(0, buffer.length);
                    const payload = JSON.stringify({ site_key: siteKey, events: batch });
                    const ep = apiBase + '/telemetry';
                    if (navigator.sendBeacon && document.visibilityState === 'hidden') {
                        navigator.sendBeacon(ep, new Blob([payload], { type: 'text/plain' }));
                    } else {
                        fetch(ep, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, keepalive: true })
                            .then(r => r.json()).then(d => log("Sincronizado (" + d.stored + " eventos)"))
                            .catch(() => {});
                    }
                } catch(e) {}
            }

            setInterval(flush, 4000);

            document.addEventListener('visibilitychange', function() {
                if (document.visibilityState === 'visible') { startTime = Date.now(); isVis = true; }
                else { if (isVis) dwellMs += Date.now() - startTime; isVis = false; flush(); }
            });
            window.addEventListener('beforeunload', function() {
                const total = isVis ? dwellMs + (Date.now() - startTime) : dwellMs;
                buffer.push({ event_type: 'page_dwell', page_url: window.location.href, event_data: { active_dwell_ms: total } });
                flush();
            });

            window.addEventListener('load', function() {
                setTimeout(function() {
                    const nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
                    emit('web_vitals', {
                        ttfb_ms: nav ? Math.round(nav.responseStart - nav.requestStart) : 0,
                        load_time_ms: nav ? Math.round(nav.loadEventEnd - nav.startTime) : 0
                    }, false);
                }, 100);
            });

            window.addEventListener('error', function(e) {
                emit('client_error', { message: e.message, file: e.filename, line: e.lineno }, true);
            });

            document.addEventListener('click', function(e) {
                const el = e.target;
                const id = el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + String(el.className).split(' ')[0] : '');
                const rawText = (el.innerText || '').slice(0, 35).trim();
                const safeText = isSensitive(el) ? '[REDACTED_PII]' : rawText;
                emit('click', { element: id, text: safeText, dataset: Object.assign({}, el.dataset) });
            }, true);

            window.WolfAnalytics = window.Counter = { track: (t, d, imm) => emit(t, d, imm), flush: flush };
        }
    } catch (globalErr) {}
})();
