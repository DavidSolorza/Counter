package com.counter.security.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Entidad JPA para la tabla client_licenses en security.db.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@Entity
@Table(name = "client_licenses")
public class ClientLicense {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_name", nullable = false)
    private String clientName;

    @Column(name = "site_key", nullable = false, unique = true)
    private String siteKey;

    @Column(name = "secret_token")
    private String secretToken;

    @Column(name = "allowed_domain", nullable = false)
    private String allowedDomain;

    @Column(name = "monthly_quota", nullable = false)
    private Integer monthlyQuota = 100000;

    @Column(name = "is_active", nullable = false)
    private Integer isActive = 1;

    @Column(name = "tier", nullable = false)
    private String tier = "ENTERPRISE";

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", insertable = false, updatable = false)
    private LocalDateTime updatedAt;

    public ClientLicense() {}

    public ClientLicense(String clientName, String siteKey, String allowedDomain, Integer isActive) {
        this.clientName = clientName;
        this.siteKey = siteKey;
        this.allowedDomain = allowedDomain;
        this.isActive = isActive;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getClientName() { return clientName; }
    public void setClientName(String clientName) { this.clientName = clientName; }

    public String getSiteKey() { return siteKey; }
    public void setSiteKey(String siteKey) { this.siteKey = siteKey; }

    public String getSecretToken() { return secretToken; }
    public void setSecretToken(String secretToken) { this.secretToken = secretToken; }

    public String getAllowedDomain() { return allowedDomain; }
    public void setAllowedDomain(String allowedDomain) { this.allowedDomain = allowedDomain; }

    public Integer getMonthlyQuota() { return monthlyQuota; }
    public void setMonthlyQuota(Integer monthlyQuota) { this.monthlyQuota = monthlyQuota; }

    public Integer getIsActive() { return isActive; }
    public void setIsActive(Integer isActive) { this.isActive = isActive; }

    public String getTier() { return tier; }
    public void setTier(String tier) { this.tier = tier; }

    public boolean isLicenseActive() { return this.isActive != null && this.isActive == 1; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
