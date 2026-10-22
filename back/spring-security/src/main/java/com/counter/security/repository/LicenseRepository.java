package com.counter.security.repository;

import com.counter.security.domain.ClientLicense;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

/**
 * Repositorio Spring Data JPA para client_licenses.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@Repository
public interface LicenseRepository extends JpaRepository<ClientLicense, Long> {

    Optional<ClientLicense> findBySiteKey(String siteKey);

    boolean existsBySiteKey(String siteKey);
}
