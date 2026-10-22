package com.counter.security.service;

import com.counter.security.domain.ClientLicense;
import com.counter.security.repository.LicenseRepository;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.*;

@Service
public class GithubAuthService {
    private final LicenseRepository licenseRepository;
    private final SecurityService securityService;
    private final HttpClient httpClient;

    public GithubAuthService(LicenseRepository licenseRepository, SecurityService securityService) {
        this.licenseRepository = licenseRepository;
        this.securityService = securityService;
        this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(6)).build();
    }

    public Map<String, Object> authenticateGithub(Map<String, String> payload) {
        String code = payload.get("code");
        String username = payload.get("username");
        String email = payload.get("email");
        String avatarUrl = payload.get("avatar_url");
        String role = payload.getOrDefault("role", "admin");

        if ((username == null || username.trim().isEmpty() || "DavidSolorza".equals(username)) && code != null && !code.trim().isEmpty()) {
            Map<String, String> ghUser = fetchGithubProfile(code.trim());
            if (ghUser.containsKey("username")) {
                username = ghUser.get("username");
                email = ghUser.get("email");
                avatarUrl = ghUser.get("avatar_url");
            }
        }

        if (username == null || username.trim().isEmpty()) username = "DavidSolorza";
        if (avatarUrl == null || avatarUrl.trim().isEmpty()) avatarUrl = "https://github.com/" + username + ".png";
        if (email == null || email.trim().isEmpty()) email = username.toLowerCase() + "@github.local";

        ClientLicense license = resolveLicenseForUser(username);
        String sessionToken = "cntr_sess_" + UUID.randomUUID().toString().replace("-", "");

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("token", sessionToken);

        Map<String, Object> user = new HashMap<>();
        user.put("username", username);
        user.put("email", email);
        user.put("avatar_url", avatarUrl);
        user.put("role", role);
        user.put("provider", "github");
        resp.put("user", user);

        Map<String, Object> lic = new HashMap<>();
        lic.put("site_key", license.getSiteKey());
        lic.put("client_name", license.getClientName());
        lic.put("allowed_domain", license.getAllowedDomain());
        lic.put("is_active", license.getIsActive());
        resp.put("license", lic);
        return resp;
    }

    private ClientLicense resolveLicenseForUser(String username) {
        Optional<ClientLicense> existing = licenseRepository.findFirstByClientNameIgnoreCase(username);
        if (existing.isPresent()) return existing.get();

        String safeName = username.toLowerCase().replaceAll("[^a-z0-9]", "");
        String newKey = securityService.generateSiteKey("cntr_" + safeName + "_");
        ClientLicense created = new ClientLicense(username, newKey, "*", 1);
        return licenseRepository.save(created);
    }

    private Map<String, String> fetchGithubProfile(String code) {
        Map<String, String> data = new HashMap<>();
        try {
            String token = code;
            if (!code.startsWith("ghp_") && !code.startsWith("gho_")) {
                String exchanged = exchangeOAuthCode(code);
                if (exchanged != null && !exchanged.isEmpty()) token = exchanged;
            }
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://api.github.com/user"))
                    .header("User-Agent", "Counter-Intelligence-OAuth")
                    .header("Accept", "application/vnd.github.v3+json")
                    .header("Authorization", "Bearer " + token)
                    .GET()
                    .build();
            HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200 && resp.body().contains("\"login\":")) {
                data.put("username", extractJsonField(resp.body(), "login"));
                data.put("avatar_url", extractJsonField(resp.body(), "avatar_url"));
                data.put("email", extractJsonField(resp.body(), "email"));
            }
        } catch (Exception ignored) {}
        return data;
    }

    private String exchangeOAuthCode(String code) {
        try {
            String json = String.format("{\"client_id\":\"%s\",\"client_secret\":\"%s\",\"code\":\"%s\"}",
                    "Ov23liCRgpOkJdEvTFzO", "7b26c3e8d4f6162b8c3905d5777be78c129febc6", code);
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://github.com/login/oauth/access_token"))
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json))
                    .build();
            HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) return extractJsonField(resp.body(), "access_token");
        } catch (Exception ignored) {}
        return null;
    }

    private String extractJsonField(String json, String field) {
        try {
            String marker = "\"" + field + "\":\"";
            int idx = json.indexOf(marker);
            if (idx == -1) return null;
            int start = idx + marker.length();
            int end = json.indexOf("\"", start);
            return end != -1 ? json.substring(start, end) : null;
        } catch (Exception e) { return null; }
    }
}
