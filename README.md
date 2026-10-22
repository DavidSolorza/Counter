# 🐺 Counter Platform: Enterprise Telemetry & Security Engine

Plataforma de inteligencia de usuario, telemetría pasiva en tiempo real y pasarela de seguridad B2B con arquitectura desacoplada de microservicios.

---

## 🏛️ Arquitectura Dual de Microservicios

1. **Spring Boot Security (:8080):** Gobernanza, autenticación GitHub OAuth, licenciamiento B2B, generación criptográfica de Site Keys y Kill Switch.
2. **Flask Analytics Engine (:5000):** Ingesta masiva de telemetría pasiva (`counter.js`), análisis de fricción (rage clicks, u-turns) y mapas de calor.

---

## 🚀 Inicio Rápido en Local (SQLite Zero-Config)

Para desarrollo ágil en local, el sistema utiliza SQLite embebido sin dependencias externas:

```bash
# 1. Arrancar Microservicio de Seguridad (Spring Boot)
cd back/spring-security
mvn spring-boot:run

# 2. Arrancar Microservicio de Analítica (Flask)
cd back/flask-analytics
python app.py
```

- Portal y Dashboard: `http://localhost:5000/dashboard`
- API Seguridad: `http://localhost:8080/api/v1/security/health`
- API Analítica: `http://localhost:5000/health`

---

## ☁️ Despliegue y Montaje en Producción (PostgreSQL)

Al desplegar en la nube (**Supabase**, **Neon**, **AWS RDS**, **Railway** o **Docker**), se utiliza la base de datos canónica relacional PostgreSQL 15+.

### 1. Ejecutar Scripts SQL en Orden Estricto:
```bash
psql -U postgres -d counter_db -f docs/database/production/01_security_postgres_schema.sql
psql -U postgres -d counter_db -f docs/database/production/02_analytics_postgres_schema.sql
psql -U postgres -d counter_db -f docs/database/production/03_seed_production_data.sql
```

### 2. Configurar Variables de Entorno en Producción:
- **Spring Boot:** Reemplazar `url: jdbc:sqlite:security.db` por `jdbc:postgresql://[HOST]:5432/counter_db`.
- **Flask:** Configurar `DATABASE_URL=postgresql://[USER]:[PASS]@[HOST]:5432/counter_db`.

> Para ver la guía completa paso a paso, consulta [docs/manual/GUIA_DESPLIEGUE_PRODUCCION.md](file:///c:/Users/Usuario/Desktop/Counter/docs/manual/GUIA_DESPLIEGUE_PRODUCCION.md).

---

## 📁 Estructura del Repositorio
- `back/spring-security/`: Microservicio Spring Boot 3.x (Java 17+).
- `back/flask-analytics/`: Microservicio Flask Analytics (Python 3.10+).
- `docs/database/production/`: Esquemas DDL canónicos para PostgreSQL.
- `docs/manual/`: Manuales de usuario y guías de despliegue.
- `docs/proposals/`: Registros de arquitectura y propuestas de gobernanza.
