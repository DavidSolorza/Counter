/**
 * sdk/modules/visibility_tracker.js
 * Monitoreo de tiempo activo y descarte de pestañas inactivas/minimizadas.
 * Gobernanza: Límite estricto < 150 líneas.
 */
export function createVisibilityTracker() {
    let activeStartTime = Date.now();
    let totalDwellMs = 0;
    let isVisible = document.visibilityState === 'visible';

    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            activeStartTime = Date.now();
            isVisible = true;
        } else {
            if (isVisible) {
                totalDwellMs += Date.now() - activeStartTime;
            }
            isVisible = false;
        }
    });

    return {
        getActiveDwellMs: function() {
            if (isVisible) {
                return totalDwellMs + (Date.now() - activeStartTime);
            }
            return totalDwellMs;
        }
    };
}
