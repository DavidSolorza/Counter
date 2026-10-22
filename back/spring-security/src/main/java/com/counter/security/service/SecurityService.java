package com.counter.security.service;

import com.counter.security.domain.ClientLicense;
import com.counter.security.repository.LicenseRepository;
import org.springframework.stereotype.Service;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Optional;

/**
 * Servicio de seguridad para generación de llaves y validación de licencias.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@Service
public class SecurityService {

    private final LicenseRepository licenseRepository;
    private static final String CHARS = "abcdefghijklmnopqrstuvwxyz0123456789";
    private final SecureRandom random = new SecureRandom();

    public SecurityService(LicenseRepository licenseRepository) {
        this.licenseRepository = licenseRepository;
    }

    public String generateSiteKey(String prefix) {
        StringBuilder sb = new StringBuilder(prefix != null ? prefix : "wk_live_");
        for (int i = 0; i < 24; i++) {
            sb.append(CHARS.charAt(random.nextInt(CHARS.length())));
        }
        return sb.toString();
    }

    public boolean isDomainAllowed(String incomingDomain, String allowedPattern) {
        if (allowedPattern == null || allowedPattern.trim().isEmpty()) return true;
        if (incomingDomain == null || incomingDomain.trim().isEmpty()) return false;

        String cleanHost = incomingDomain.toLowerCase().replaceAll(":[0-9]+$", "").trim();
        String[] allowedList = allowedPattern.toLowerCase().split(",");

        return Arrays.stream(allowedList)
                .map(String::trim)
                .anyMatch(allowed -> allowed.equals("*") || allowed.equals(cleanHost) || 
                        (allowed.startsWith("*.") && cleanHost.endsWith(allowed.substring(1))) ||
                        (cleanHost.equals("127.0.0.1") && allowed.equals("localhost")) ||
                        (cleanHost.equals("localhost") && allowed.equals("127.0.0.1")));
    }

    public Optional<ClientLicense> findLicense(String siteKey) {
        if (siteKey == null || siteKey.trim().isEmpty()) return Optional.empty();
        return licenseRepository.findBySiteKey(siteKey.trim());
    }
}
