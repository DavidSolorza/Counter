package com.counter.security.service;

import com.counter.security.domain.ClientLicense;
import com.counter.security.repository.LicenseRepository;
import org.springframework.stereotype.Service;
import java.security.SecureRandom;
import java.text.Normalizer;
import java.util.*;

/**
 * Servicio de seguridad para generación de llaves, validación de licencias
 * y resolución centralizada de identidad multi-proveedor (Google / GitHub).
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

    public String normalizeIdentity(String input) {
        if (input == null) return "";
        String decomposed = Normalizer.normalize(input.trim(), Normalizer.Form.NFD);
        return decomposed.replaceAll("\\p{InCombiningDiacriticalMarks}+", "")
                .toLowerCase()
                .replaceAll("[^a-z0-9]", "");
    }

    public synchronized ClientLicense resolveUnifiedLicense(String primaryName, String altName, String email) {
        Set<String> candidateKeys = new LinkedHashSet<>();
        String normPrimary = normalizeIdentity(primaryName);
        String normAlt = normalizeIdentity(altName);
        if (!normPrimary.isEmpty()) candidateKeys.add(normPrimary);
        if (!normAlt.isEmpty()) candidateKeys.add(normAlt);
        if (email != null && email.contains("@")) {
            String localPart = normalizeIdentity(email.split("@")[0]);
            if (!localPart.isEmpty()) candidateKeys.add(localPart);
        }

        List<ClientLicense> allLicenses = licenseRepository.findAll();
        for (ClientLicense lic : allLicenses) {
            String licNormName = normalizeIdentity(lic.getClientName());
            if (!licNormName.isEmpty() && candidateKeys.contains(licNormName)) {
                return lic;
            }
            if (lic.getSiteKey() != null) {
                String sk = lic.getSiteKey().toLowerCase();
                for (String key : candidateKeys) {
                    if (key.length() >= 3 && (sk.startsWith("cntr_" + key + "_") || sk.startsWith("cntr_google_" + key + "_"))) {
                        return lic;
                    }
                }
            }
        }

        String displayName = (primaryName != null && !primaryName.trim().isEmpty()) ? primaryName.trim() : "Counter User";
        String safeKey = normPrimary.isEmpty() ? "user" : normPrimary;
        String newSiteKey = generateSiteKey("cntr_" + safeKey + "_");
        ClientLicense created = new ClientLicense(displayName, newSiteKey, "*", 1);
        created.setSecretToken(generateSiteKey("cntr_sec_"));
        created.setMonthlyQuota(100000);
        created.setTier("ENTERPRISE");
        return licenseRepository.save(created);
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
        String cleanKey = siteKey.trim();
        Optional<ClientLicense> exact = licenseRepository.findBySiteKey(cleanKey);
        if (exact.isPresent()) return exact;

        String lower = cleanKey.toLowerCase();
        if (lower.startsWith("cntr_")) {
            String[] parts = lower.split("_");
            String identity = (parts.length >= 3 && "google".equals(parts[1])) ? parts[2] : (parts.length >= 2 ? parts[1] : "");
            if (identity.length() >= 3) {
                for (ClientLicense lic : licenseRepository.findAll()) {
                    if (normalizeIdentity(lic.getClientName()).equals(identity) ||
                        (lic.getSiteKey() != null && lic.getSiteKey().toLowerCase().startsWith("cntr_" + identity + "_"))) {
                        return Optional.of(lic);
                    }
                }
            }
        }
        return Optional.empty();
    }
}
