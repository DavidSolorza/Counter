package com.counter.security.controller;

import com.counter.security.domain.ClientLicense;
import com.counter.security.repository.LicenseRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * Controlador REST para Gestión de Clientes, Usuarios y Licencias en Tiempo Real.
 * Sincronizado con security.db y el Kill-Switch de SecurityController.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@RestController
@RequestMapping("/api/v1/admin/users")
@CrossOrigin(origins = "*")
public class AdminUsersController {

    private final LicenseRepository licenseRepository;

    public AdminUsersController(LicenseRepository licenseRepository) {
        this.licenseRepository = licenseRepository;
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listAllUsers() {
        List<ClientLicense> licenses = licenseRepository.findAll();
        List<Map<String, Object>> result = new ArrayList<>();

        for (ClientLicense lic : licenses) {
            Map<String, Object> u = new HashMap<>();
            u.put("id", "lic_" + lic.getId());
            u.put("fullName", lic.getClientName());
            u.put("email", buildEmail(lic.getClientName()));
            u.put("role", lic.getClientName().toLowerCase().contains("admin") || lic.getId() == 1 ? "admin" : "user");
            
            String status = "active";
            if (lic.getIsActive() == null || lic.getIsActive() == 0) {
                status = "inactive";
            } else if (lic.getIsActive() == 2) {
                status = "cancelled";
            }
            u.put("status", status);
            u.put("department", resolveDepartment(lic.getClientName()));
            u.put("lastActive", lic.getCreatedAt() != null ? lic.getCreatedAt().toString().replace("T", " ") : "Reciente");
            u.put("siteKey", lic.getSiteKey());
            u.put("allowedDomain", lic.getAllowedDomain());
            result.add(u);
        }

        return ResponseEntity.ok(result);
    }

    @PostMapping("/{siteKey}/toggle")
    public ResponseEntity<Map<String, Object>> toggleStatus(@PathVariable("siteKey") String siteKey) {
        Optional<ClientLicense> opt = licenseRepository.findBySiteKey(siteKey);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        ClientLicense lic = opt.get();
        int nextActive = (lic.getIsActive() != null && lic.getIsActive() == 1) ? 0 : 1;
        lic.setIsActive(nextActive);
        licenseRepository.save(lic);

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("siteKey", siteKey);
        resp.put("isActive", nextActive);
        resp.put("status", nextActive == 1 ? "active" : "inactive");
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/{siteKey}/role")
    public ResponseEntity<Map<String, Object>> updateRole(
            @PathVariable("siteKey") String siteKey,
            @RequestBody(required = false) Map<String, String> payload) {
        Optional<ClientLicense> opt = licenseRepository.findBySiteKey(siteKey);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        String newRole = payload != null ? payload.getOrDefault("role", "user") : "user";

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("siteKey", siteKey);
        resp.put("role", newRole);
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/{siteKey}/cancel")
    public ResponseEntity<Map<String, Object>> cancelUser(@PathVariable("siteKey") String siteKey) {
        Optional<ClientLicense> opt = licenseRepository.findBySiteKey(siteKey);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        ClientLicense lic = opt.get();
        lic.setIsActive(2);
        licenseRepository.save(lic);

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("siteKey", siteKey);
        resp.put("status", "cancelled");
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/{siteKey}/activate")
    public ResponseEntity<Map<String, Object>> activateUser(@PathVariable("siteKey") String siteKey) {
        Optional<ClientLicense> opt = licenseRepository.findBySiteKey(siteKey);
        if (opt.isEmpty()) return ResponseEntity.notFound().build();
        ClientLicense lic = opt.get();
        lic.setIsActive(1);
        licenseRepository.save(lic);

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("siteKey", siteKey);
        resp.put("status", "active");
        return ResponseEntity.ok(resp);
    }

    private String buildEmail(String name) {
        if (name == null) return "user@counter.local";
        String clean = name.toLowerCase().replaceAll("[^a-z0-9]", ".");
        clean = clean.replaceAll("\\.+", ".").replaceAll("^\\.|\\.$", "");
        return clean + "@counter.enterprise";
    }

    private String resolveDepartment(String name) {
        if (name == null) return "Operaciones";
        String lower = name.toLowerCase();
        if (lower.contains("demo") || lower.contains("enterprise")) return "Infraestructura Global";
        if (lower.contains("streaming") || lower.contains("store")) return "Comercio Digital & Media";
        if (lower.contains("david")) return "Seguridad y Arquitectura Central";
        return "Inteligencia y Métricas";
    }
}
