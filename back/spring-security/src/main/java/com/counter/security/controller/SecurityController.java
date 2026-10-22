package com.counter.security.controller;

import com.counter.security.domain.ClientLicense;
import com.counter.security.service.SecurityService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Controlador REST para Handshake de seguridad y Kill Switch.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@RestController
@RequestMapping("/api/v1/security")
@CrossOrigin(origins = "*")
public class SecurityController {

    private final SecurityService securityService;

    public SecurityController(SecurityService securityService) {
        this.securityService = securityService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("status", "UP");
        resp.put("service", "Counter Security Microservice");
        resp.put("port", 8080);
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/verify")
    public ResponseEntity<Map<String, Object>> verify(@RequestBody Map<String, String> payload) {
        Map<String, Object> resp = new HashMap<>();
        String siteKey = payload.get("site_key");
        String domain = payload.get("domain");

        if (siteKey == null || siteKey.trim().isEmpty()) {
            resp.put("valid", false);
            resp.put("error", "Site Key ausente en la petición.");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(resp);
        }

        Optional<ClientLicense> licenseOpt = securityService.findLicense(siteKey);
        if (licenseOpt.isEmpty()) {
            resp.put("valid", false);
            resp.put("error", "Licencia no registrada en el sistema.");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(resp);
        }

        ClientLicense license = licenseOpt.get();

        // 1. Validación de Kill Switch (is_active)
        if (!license.isLicenseActive()) {
            resp.put("valid", false);
            resp.put("error", "Licencia suspendida o inactiva (Kill Switch activo).");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(resp);
        }

        // 2. Validación de Dominio (Domain Locking)
        if (domain != null && !securityService.isDomainAllowed(domain, license.getAllowedDomain())) {
            resp.put("valid", false);
            resp.put("error", "Dominio '" + domain + "' no autorizado para esta Site Key.");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(resp);
        }

        resp.put("valid", true);
        resp.put("client_name", license.getClientName());
        resp.put("site_key", license.getSiteKey());
        resp.put("allowed_domain", license.getAllowedDomain());
        resp.put("message", "Licencia verificada exitosamente.");
        return ResponseEntity.ok(resp);
    }
}
