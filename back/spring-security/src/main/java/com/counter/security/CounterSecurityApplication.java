package com.counter.security;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Microservicio de Seguridad y Licencias Counter.
 * Gobernanza: Límite estricto < 150 líneas.
 */
@SpringBootApplication
public class CounterSecurityApplication {

    public static void main(String[] args) {
        SpringApplication.run(CounterSecurityApplication.class, args);
    }
}
