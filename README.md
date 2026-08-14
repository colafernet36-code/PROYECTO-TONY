# Proyecto TONY

[![CI](https://github.com/colafernet36-code/PROYECTO-TONY/actions/workflows/ci.yml/badge.svg)](https://github.com/colafernet36-code/PROYECTO-TONY/actions/workflows/ci.yml)

Asistente personal inteligente, local-first, modular, seguro y extensible — para conversar,
recordar, investigar, colaborar, automatizar y controlar sistemas autorizados bajo supervisión
humana.

Este repositorio implementa la arquitectura definida en `docs/architecture/` (v0.1 visión, v0.2
arquitectura técnica, v0.3 baseline vigente). **v0.3 es la fuente de verdad**; cualquier cambio
de arquitectura debe registrarse como un ADR nuevo en `docs/adr/`, no como una edición
silenciosa del código.

## Estado actual: hito v0.0.1 — Core Bootstrap

Implementado y verificado en Linux (v0.3 §20):

```text
Kali Linux -> systemd -> TONY Core Bootstrap -> PostgreSQL -> Event Bus
           -> Audit Service -> publish: system.tony_ready
```

Ver el detalle de qué se construyó y qué queda deliberadamente fuera de alcance en
`docs/adr/0001-bootstrap-v0.0.1.md`.

## Arranque rápido en Linux

```bash
# PostgreSQL de desarrollo
docker compose up -d postgres   # o: sudo service postgresql start

# Entorno Python
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Configuracion y migraciones
cp .env.example .env
alembic upgrade head

# Arrancar TONY
tony
```

Instrucciones completas de instalación como servicio systemd, diagnóstico y solución de
problemas: `docs/operations/RUNBOOK.md`.

## Estructura del repositorio

La estructura completa está definida en `docs/architecture/especificacion-v0.3.md` §16. Cada
carpeta trae su propio `README.md`:

- Si ya tiene código, el `README.md`/docstring del módulo explica su responsabilidad actual.
- Si todavía no está implementada, el `README.md` indica qué hará y en qué paso del "orden
  oficial de implementación" (v0.3 §19) se activa.

Piezas ya implementadas en este hito:

| Carpeta | Contenido |
|---|---|
| `contracts/` | Modelos compartidos: `Action`, `ToolCall`, `RiskLevel`, `AuthorizationGrant`, `AuditEvent`, `SystemEvent`, etc. |
| `core/event_bus/` | Event Bus asíncrono en proceso |
| `core/bootstrap/` | Secuencia de arranque de TONY Core (entry point `tony`) |
| `config/` | Configuración desde `.env` (pydantic-settings) |
| `database/` | Modelos SQLAlchemy, migraciones Alembic, repositorio de auditoría |
| `audit/` | Audit Service (registro append-only) |
| `systemd/units/tony.service` | Unidad systemd con hardening de seguridad |
| `scripts/install/`, `scripts/diagnostics/` | Instalación en Kali/Debian y diagnóstico |
| `tests/` | Unitarios (`core/event_bus`, `contracts`) e integración (bootstrap contra PostgreSQL real) |

Todo lo demás (Policy Engine, AI Router, memoria, voz, agentes, UI, domótica, autenticación
reforzada con iPhone/Face ID, hardening) corresponde a los pasos siguientes del orden oficial
de implementación y está deliberadamente sin implementar todavía — construir sobre eso antes de
verificar este hito violaría la regla de desarrollo de la propia especificación.

## Tests

```bash
pytest tests/unit tests/integration
```

Los tests de integración requieren `DATABASE_URL` (o `TEST_DATABASE_URL`) apuntando a un
PostgreSQL real; se saltan automáticamente si no hay uno disponible.

GitHub Actions corre esta misma batería (con un PostgreSQL de servicio) en cada push a `main`
y en cada pull request — ver `.github/workflows/ci.yml`.

## Principios no negociables (v0.1 §2)

Control humano · Seguridad por diseño · Arquitectura modular · Memoria controlable ·
Trazabilidad · Degradación segura.
