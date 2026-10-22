package com.counter.security.controller;

import com.counter.security.service.GithubAuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Controlador REST para Autenticación con GitHub (OAuth 2.0).
 * Gobernanza: Límite estricto < 150 líneas.
 */
@RestController
@RequestMapping("/api/v1/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final GithubAuthService githubAuthService;

    public AuthController(GithubAuthService githubAuthService) {
        this.githubAuthService = githubAuthService;
    }

    @PostMapping("/github")
    public ResponseEntity<Map<String, Object>> loginWithGithub(@RequestBody(required = false) Map<String, String> payload) {
        if (payload == null) {
            payload = new HashMap<>();
        }
        Map<String, Object> authResponse = githubAuthService.authenticateGithub(payload);
        return ResponseEntity.ok(authResponse);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> authHealth() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("service", "Counter Security Auth API");
        resp.put("provider", "github");
        resp.put("status", "UP");
        return ResponseEntity.ok(resp);
    }
}
