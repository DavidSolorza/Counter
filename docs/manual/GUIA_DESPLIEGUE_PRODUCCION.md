# 🚀 Guía de Despliegue y Montaje en Producción: Counter Platform

Esta guía detalla el procedimiento oficial para aprovisionar, montar la base de datos canónica y poner en marcha los microservicios de **Counter** en entornos de nube (**Supabase**, **Neon**, **AWS RDS**, **Railway**, **Render** o contenedores **Docker**).

---

## 1. Aprovisionamiento y Montaje de Base de Datos (PostgreSQL)

Counter utiliza **PostgreSQL 15+** como motor relacional de grado empresarial para producción. Los esquemas DDL canónicos se encuentran centralizados en `docs/database/production/`.

Ejecuta los scripts en el orden cronológico estricto:

```bash
# 1. Esquema de Seguridad (Spring Boot: licencias, usuarios, OAuth GitHub y auditoría)
psql -U postgres -h [DB_HOST] -d counter_db -f docs/database/production/01_security_postgres_schema.sql

# 2. Esquema de Analítica (Flask: telemetría JSONB, índices GIN y agregados de sesión)
psql -U postgres -h [DB_HOST] -d counter_db -f docs/database/production/02_analytics_postgres_schema.sql

# 3. Inserción de Semillas Iniciales (Licencias demo y usuario administrador inicial)
psql -U postgres -h [DB_HOST] -d counter_db -f docs/database/production/03_seed_production_data.sql
```

> [!NOTE]
> En servicios administrados como **Supabase** o **Neon**, puedes copiar y pegar el contenido de los 3 archivos en el editor SQL web (SQL Editor) en el mismo orden correlativo.

---

## 2. Variables de Entorno para Microservicios

### Microservicio 1: Spring Boot Security (:8080)
Sustituir el driver y URL de SQLite local (`jdbc:sqlite:security.db`) por las credenciales de PostgreSQL en `application.yml` o mediante variables de entorno del contenedor:

```bash
SPRING_DATASOURCE_URL=jdbc:postgresql://[DB_HOST]:5432/counter_db
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=[TU_PASSWORD_SEGURO]
SPRING_JPA_DATABASE_PLATFORM=org.hibernate.dialect.PostgreSQLDialect
SPRING_JPA_HIBERNATE_DDL_AUTO=validate
GITHUB_CLIENT_ID=[TU_GITHUB_CLIENT_ID]
GITHUB_CLIENT_SECRET=[TU_GITHUB_CLIENT_SECRET]
```

### Microservicio 2: Flask Analytics Engine (:5000)
Configurar la variable de conexión de base de datos en el entorno o archivo `.env`:

```bash
DATABASE_URL=postgresql://postgres:[TU_PASSWORD_SEGURO]@[DB_HOST]:5432/counter_db
PORT=5000
FLASK_ENV=production
```

---

## 3. Verificación de Salud Post-Despliegue

Una vez levantados los servicios, valida su estado mediante sus endpoints de salud:

```bash
# Verificación de Seguridad (Spring Boot)
curl -X GET http://[DOMINIO_BACKEND]:8080/api/v1/security/health

# Verificación de Analítica (Flask)
curl -X GET http://[DOMINIO_BACKEND]:5000/health
```

Respuesta esperada: `{"status": "UP"}` en ambos microservicios.
