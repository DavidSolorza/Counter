package com.counter.security.controller;

import com.counter.security.service.GithubAuthService;
import com.counter.security.service.GoogleAuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Controlador REST para Autenticación Multi-Proveedor (GitHub & Google OAuth 2.0).
 * Gobernanza: Límite estricto < 150 líneas.
 */
@RestController
@RequestMapping("/api/v1/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final GithubAuthService githubAuthService;
    private final GoogleAuthService googleAuthService;

    public AuthController(GithubAuthService githubAuthService, GoogleAuthService googleAuthService) {
        this.githubAuthService = githubAuthService;
        this.googleAuthService = googleAuthService;
    }

    @PostMapping("/github")
    public ResponseEntity<Map<String, Object>> loginWithGithub(@RequestBody(required = false) Map<String, String> payload) {
        if (payload == null) payload = new HashMap<>();
        return ResponseEntity.ok(githubAuthService.authenticateGithub(payload));
    }

    @PostMapping("/google")
    public ResponseEntity<Map<String, Object>> loginWithGoogle(@RequestBody(required = false) Map<String, String> payload) {
        if (payload == null) payload = new HashMap<>();
        return ResponseEntity.ok(googleAuthService.authenticateGoogle(payload));
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> authHealth() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("service", "Counter Security Auth API");
        resp.put("providers", new String[]{"github", "google"});
        resp.put("status", "UP");
        return ResponseEntity.ok(resp);
    }
}
