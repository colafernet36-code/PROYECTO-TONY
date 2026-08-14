# RUNBOOK — Operar TONY en Linux

## Requisitos

- Kali Linux / Debian / Ubuntu (systemd).
- Python 3.11+.
- PostgreSQL 14+ (16 recomendado; pgvector se agrega en el hito de memoria semántica, aún no
  activo).

## Desarrollo local (sin instalar como servicio)

```bash
# 1. Levantar PostgreSQL de desarrollo (o usar uno ya instalado en el sistema)
docker compose up -d postgres
# alternativa sin Docker: sudo service postgresql start

# 2. Entorno Python
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Configuracion
cp .env.example .env
# editar .env si tu Postgres no usa usuario/clave "tony"/"tony"

# 4. Migraciones
alembic upgrade head

# 5. Arrancar TONY (foreground, Ctrl+C para detener)
tony
# equivalente: python -m core.bootstrap.bootstrap
```

Deberías ver en el log: `TONY bootstrap iniciando`, luego `event system.tony_ready ...` y
`TONY READY`.

## Verificar el hito v0.0.1

```bash
pytest tests/unit tests/integration
./scripts/diagnostics/health_check.sh
```

`tests/integration` se salta automáticamente si no encuentra PostgreSQL en `DATABASE_URL`/
`TEST_DATABASE_URL`.

## Instalación como servicio (systemd)

```bash
sudo ./scripts/install/install_kali.sh /opt/tony
sudo systemctl start tony.service
journalctl -u tony.service -f
```

El script crea un usuario de servicio `tony` sin privilegios, un rol/base PostgreSQL
dedicados, genera `/opt/tony/.env` con una contraseña aleatoria, aplica las migraciones e
instala/habilita la unidad `tony.service` (ver `systemd/units/tony.service` para el hardening
aplicado).

## Solución de problemas

- **`system.degraded` / salida con código 1 al arrancar**: PostgreSQL no responde. Verificar
  `pg_isready`, que `DATABASE_URL` apunte a la base correcta y que el rol tenga permisos.
- **`tony.service` no arranca**: `journalctl -u tony.service -e` para el motivo; revisar que
  `/opt/tony/.env` exista y que `postgresql.service` esté activo (`Requires=postgresql.service`
  en la unidad).
- **Migraciones fallan**: correr `alembic upgrade head` manualmente desde `/opt/tony` con el
  venv del servicio para ver el traceback completo.

## Qué NO hace todavía este hito

No hay voz, no hay Policy Engine, no hay AI Router, no hay memoria ni agentes de terminal/
domótica: eso corresponde a los pasos 7 en adelante del orden oficial de implementación
(`docs/architecture/especificacion-v0.3.md` §19), listados también en
`docs/adr/0001-bootstrap-v0.0.1.md`. Este hito sólo prueba que el Core arranca, se conecta a
PostgreSQL, tiene Event Bus y deja auditoría — la base sobre la que se construye todo lo demás.
