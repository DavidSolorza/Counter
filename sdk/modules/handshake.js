/**
 * sdk/modules/handshake.js
 * Módulo de validación y handshake de licencia contra el backend.
 * Gobernanza: Límite estricto < 150 líneas.
 */
export function verifySiteKey(apiBase, siteKey) {
    return fetch(apiBase + '/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site_key: siteKey })
    })
    .then(function(res) {
        return res.json().then(function(data) {
            return { ok: res.ok, valid: Boolean(data.valid), data: data };
        });
    })
    .catch(function(err) {
        return { ok: false, valid: false, error: err };
    });
}
