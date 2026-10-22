/**
 * Counter Dual-Microservice SDK (v3.2.0 - Spring Security + Flask Analytics)
 * Gobernanza: Límite estricto < 150 líneas.
 */
(function () {
    "use strict";
    try {
        const tag = document.currentScript || document.querySelector('script[data-site-key]');
        if (!tag) return;
        const key = tag.getAttribute('data-site-key');
        if (!key) return;

        let srcUrl;
        try { srcUrl = new URL(tag.src, window.location.href); } catch(e) { srcUrl = window.location; }
        const isSec = window.location.protocol === 'https:' || srcUrl.protocol === 'https:';
        const proto = isSec ? 'https:' : 'http:';
        const hostName = srcUrl.hostname || window.location.hostname || 'localhost';
        const secPort = srcUrl.port === '5000' ? ':8080' : (srcUrl.port ? ':' + srcUrl.port : ':8080');
        const telPort = srcUrl.port ? ':' + srcUrl.port : ':5000';

        const isDebug = tag.getAttribute('data-debug') === 'true';
        const SEC_API = tag.getAttribute('data-security-api') || (proto + '//' + hostName + secPort + '/api/v1/security');
        const TEL_API = tag.getAttribute('data-telemetry-api') || (proto + '//' + hostName + telPort + '/api/v1/telemetry/collect');
        const log = (m, d) => { if (isDebug) console.log("%c[Counter] " + m, "color: #2563eb; font-weight: bold;", d || ""); };

        let sid = sessionStorage.getItem('__cntr_sid');
        if (!sid) { sid = Math.random().toString(36).slice(2, 9) + Date.now().toString(36); sessionStorage.setItem('__cntr_sid', sid); }
        const p = new URLSearchParams(window.location.search);
        const utm = { src: p.get('utm_source'), med: p.get('utm_medium'), camp: p.get('utm_campaign'), ref: document.referrer || null };

        function isPii(el) {
            if (!el) return false;
            const t = (el.type || '').toLowerCase(), n = (el.name || el.id || '').toLowerCase();
            return t === 'password' || el.hasAttribute('data-private') || /password|card|cvv|token|secret/i.test(n);
        }

        function extractVisual(el, safeText) {
            try {
                const tagN = (el.tagName || '').toUpperCase();
                if (tagN === 'IMG') return { type: 'image', alt: (el.alt || el.title || 'Imagen').slice(0, 25), w: el.clientWidth, h: el.clientHeight };
                if (tagN === 'VIDEO' || tagN === 'IFRAME') return { type: 'video', label: (el.title || 'Video Player').slice(0, 25), w: el.clientWidth, h: el.clientHeight };
                const st = window.getComputedStyle(el);
                if (el.classList.contains('card') || tagN === 'ARTICLE') return { type: 'card', text: (el.querySelector('h1,h2,h3,h4,strong') || el).innerText.slice(0, 25).trim() };
                return { type: 'button', text: safeText, bg: st.backgroundColor, color: st.color, radius: st.borderRadius };
            } catch(e) { return null; }
        }

        // FASE 7: Handshake y Blindaje con Spring Boot (8080)
        fetch(SEC_API + '/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ site_key: key, domain: window.location.hostname })
        }).then(r => r.json()).then(res => {
            if (res.valid) {
                log("Licencia verificada por Spring Boot. Inicializando telemetría.");
                boot(key, TEL_API);
            } else {
                console.warn("[Counter Kill-Switch] Licencia inactiva o dominio rechazado:", res.error);
            }
        }).catch(() => {
            // Fallback de contingencia si el servicio de seguridad está arrancando
            boot(key, TEL_API);
        });

        function boot(siteKey, telemetryEndpoint) {
            const buf = [];
            let tStart = Date.now(), dwell = 0, isVis = document.visibilityState === 'visible', debTimer = null;
            const recentClicks = [], milestones = { '25%': false, '50%': false, '75%': false, '100%': false };

            function emit(t, d, imm) {
                try {
                    const data = Object.assign({ _sid: sid }, d);
                    buf.push({ event_type: t, page_url: window.location.href, event_data: data });
                    log("Capturado (" + t + "):", data);
                    if (imm) flush(); else { clearTimeout(debTimer); debTimer = setTimeout(flush, 1200); }
                } catch(e) {}
            }

            function flush() {
                try {
                    if (buf.length === 0) return;
                    const batch = buf.splice(0, buf.length), payload = JSON.stringify({ site_key: siteKey, events: batch });
                    if (navigator.sendBeacon && document.visibilityState === 'hidden') {
                        navigator.sendBeacon(telemetryEndpoint, new Blob([payload], { type: 'text/plain' }));
                    } else {
                        fetch(telemetryEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: payload, keepalive: true }).catch(() => {});
                    }
                } catch(e) {}
            }

            setInterval(flush, 4000);

            window.addEventListener('scroll', function() {
                const max = document.documentElement.scrollHeight - window.innerHeight;
                if (max <= 0) return;
                const pct = Math.round((window.scrollY / max) * 100);
                ['25%', '50%', '75%', '100%'].forEach(m => {
                    if (pct >= parseInt(m) && !milestones[m]) { milestones[m] = true; emit('scroll_milestone', { depth: m }); }
                });
            }, { passive: true });

            document.addEventListener('click', function(e) {
                const el = e.target, now = Date.now();
                const id = el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + String(el.className).split(' ')[0] : '');
                recentClicks.push({ id: id, time: now });
                if (recentClicks.length > 4) recentClicks.shift();
                const isRage = recentClicks.length >= 3 && (now - recentClicks[0].time < 800) && recentClicks.every(c => c.id === id);
                const text = isPii(el) ? '[REDACTED_PII]' : (el.innerText || '').slice(0, 30).trim();
                const visual = extractVisual(el, text);
                if (isRage) emit('rage_click', { element: id, text: text, clicks: recentClicks.length, visual: visual }, true);
                else emit('click', { element: id, text: text, visual: visual });
            }, true);

            window.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') { tStart = Date.now(); isVis = true; } else { if (isVis) dwell += Date.now() - tStart; isVis = false; flush(); } });
            window.addEventListener('beforeunload', () => { emit('page_dwell', { active_dwell_ms: isVis ? dwell + (Date.now() - tStart) : dwell }); flush(); });
            window.addEventListener('error', e => emit('client_error', { message: e.message, file: e.filename, line: e.lineno }, true));
            window.addEventListener('popstate', () => emit('page_view', { path: window.location.pathname, title: document.title }));
            emit('page_view', { path: window.location.pathname, title: document.title, utm: utm });
            window.Counter = { track: (t, d, imm) => emit(t, d, imm), flush: flush };
        }
    } catch(e) {}
})();
