# ADR 0001: Bootstrap v0.0.1 — Core Bootstrap en Kali Linux

- **Estado**: Aceptado
- **Fecha**: 2026-08-14
- **Contexto de la especificación**: `docs/architecture/especificacion-v0.3.md` §19-20

## Contexto

El repositorio estaba vacío. Las tres versiones de la especificación (v0.1 visión, v0.2
arquitectura técnica, v0.3 baseline técnico) ya definían el "primer hito programable" (v0.3
§20): `Kali Linux -> systemd -> TONY Core Bootstrap -> PostgreSQL -> Event Bus -> Audit
Service -> publish: system.tony_ready`, y advierten explícitamente "no se avanza al siguiente
hito hasta verificar este recorrido".

## Decisión

Se construyó exactamente ese hito (pasos 1-6 del orden oficial de implementación, v0.3 §19),
más el esqueleto completo del repositorio (v0.3 §16) para que las fases siguientes tengan un
lugar claro donde crecer sin re-litigar la estructura.

Concretamente, en esta iteración:

1. **Estructura completa del repositorio** (v0.3 §16), con un `README.md` en cada carpeta
   todavía no implementada explicando su responsabilidad (§17) y en qué paso se activa.
2. **`contracts/`**: modelos pydantic para `Action`, `ToolCall`/`ToolResult`, `RiskLevel`,
   `AuthorizationRequest`/`AuthorizationGrant`, `MemoryItem`, `AIRequest`/`AIResponse`,
   `SystemEvent`/`EventType`, `AuditEvent`, `ErrorResponse` (v0.3 §5).
3. **`core/event_bus/`**: bus pub/sub asíncrono en proceso, con soporte wildcard y aislamiento
   de fallos de un suscriptor (degradación segura, v0.1 principio 6).
4. **`config/`**: `Settings` (pydantic-settings) desde `.env`/variables de entorno.
5. **`database/`**: engine/session de SQLAlchemy 2.0, modelo `AuditEventORM`, migración Alembic
   inicial (`0001_audit_events`). Solo se migró el dominio de Auditoría (v0.3 §8): el resto de
   los dominios (identidad, conversación, memoria, proyectos, ejecución, seguridad, IA,
   automatización, domótica, sistema) se agrega junto con el paso del orden oficial que
   realmente los necesita, para no crear tablas sin código que las use.
6. **`audit/`**: `AuditService` + `DBAuditWriter`, repositorio append-only (sin `update`/
   `delete` expuestos).
7. **`core/bootstrap/`**: secuencia de arranque real — carga config, `SELECT 1` contra
   PostgreSQL (o `system.degraded` + salida no-cero si falla), instancia `EventBus` y
   `AuditService`, registra un `AuditEvent` de boot, publica `system.tony_ready`, y espera
   `SIGTERM`/`SIGINT` para apagarse ordenadamente bajo systemd.
8. **`systemd/units/tony.service`**: unidad con hardening (`NoNewPrivileges`,
   `ProtectSystem=strict`, `CapabilityBoundingSet=` vacío, etc. — v0.1 principio "Seguridad por
   diseño").
9. **`scripts/install/install_kali.sh`** y **`scripts/diagnostics/health_check.sh`**: instalación
   reproducible en Kali/Debian/Ubuntu (paquetes, usuario de servicio dedicado, rol/DB de
   Postgres, migraciones, unidad systemd) y diagnóstico rápido.
10. **Tests**: unitarios para `EventBus` y `contracts`, integración contra PostgreSQL real para
    el bootstrap completo (`tests/integration`, se salta si no hay base disponible).

## Explícitamente fuera de alcance de este hito

Quedan como carpetas-README para pasos posteriores del orden oficial (v0.3 §19), sin código
funcional todavía: `security/policy_engine` (paso 7), `agents/terminal` (paso 8), `ai/router`
+ proveedores (paso 9), memoria conversacional/semántica (pasos 10-11), voz (paso 12), UI
(paso 13), `security/authorization` + cliente iPhone (paso 14), `privileged-agent` en Rust
(paso 15), automatización/domótica (pasos 16-17), y hardening/backups (paso 19).

No implementar estos pasos ahora es intencional: la propia especificación exige verificar cada
hito antes de avanzar, y construir Policy Engine o AI Router sin Audit Service ya probado
violaría el orden que la arquitectura define.

## Consecuencias

- El repositorio arranca hoy de verdad en Linux: `tony` como servicio systemd o como comando
  interactivo, conecta a PostgreSQL, dejar traza de auditoría y publica `system.tony_ready`.
- El siguiente hito (Policy Engine + `RiskLevel`, paso 7) tiene ya los contratos (`RiskLevel`,
  `Action` con su máquina de estados) y el Event Bus/Audit Service sobre los que apoyarse.
- Cualquier cambio a esta decisión debe registrarse como un nuevo ADR, no como una edición
  silenciosa de este documento (regla v0.1 §10).
