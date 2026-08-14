#!/usr/bin/env bash
# Instala TONY v0.0.1 (Core Bootstrap) en Kali/Debian/Ubuntu (v0.2 S1: "Plataforma: PC
# dual-boot, primera implementacion en Kali Linux"; v0.3 S19 pasos 1-6).
#
# Revisar antes de ejecutar en una maquina real. Pensado para correr como root o con sudo.
#
# Uso:
#   sudo ./scripts/install/install_kali.sh [/ruta/de/instalacion]
#
# Por defecto instala en /opt/tony. Es idempotente en las credenciales de PostgreSQL: si ya
# existe .env, su DATABASE_URL es la fuente de verdad y el rol de PostgreSQL se sincroniza
# contra esa contraseña (via ALTER ROLE); si no existe, se genera una contraseña nueva y se
# fuerza tanto en el rol como en .env. Esto evita que una reinstalacion o una recuperacion
# parcial (p. ej. .env perdido pero el rol de PostgreSQL sobreviviendo) deje el rol y .env
# con contraseñas distintas entre si (ver docs/adr/0001-bootstrap-v0.0.1.md).

set -euo pipefail

INSTALL_DIR="${1:-/opt/tony}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICE_USER="tony"
DB_NAME="tony"
DB_USER="tony"
ENV_FILE="${INSTALL_DIR}/.env"

if [[ $EUID -ne 0 ]]; then
  echo "Este script necesita privilegios de root (usar sudo)." >&2
  exit 1
fi

echo "==> Instalando dependencias del sistema"
apt-get update
apt-get install -y \
  postgresql postgresql-contrib \
  python3 python3-venv python3-pip \
  build-essential libpq-dev

echo "==> Asegurando que PostgreSQL este activo"
systemctl enable --now postgresql

echo "==> Creando usuario de servicio '${SERVICE_USER}' (sin privilegios, minimo privilegio)"
if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "${INSTALL_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

echo "==> Copiando repositorio a ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
rsync -a --delete \
  --exclude ".git" --exclude ".venv" --exclude "__pycache__" --exclude ".env" \
  "${REPO_DIR}/" "${INSTALL_DIR}/"

echo "==> Creando entorno virtual e instalando TONY"
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/.venv/bin/pip" install -e "${INSTALL_DIR}"

echo "==> Resolviendo credenciales de PostgreSQL (idempotente)"
if [[ -f "${ENV_FILE}" ]]; then
  EXISTING_URL="$(grep -E '^DATABASE_URL=' "${ENV_FILE}" | head -n1 | cut -d= -f2-)"
  if [[ "${EXISTING_URL}" =~ ^postgresql\+psycopg://${DB_USER}:([^@]+)@ ]]; then
    DB_PASSWORD="${BASH_REMATCH[1]}"
    WRITE_ENV=false
    echo "    ${ENV_FILE} ya existe: se reutiliza su contraseña como fuente de verdad."
  else
    echo "No se pudo leer una contraseña valida para '${DB_USER}' desde ${ENV_FILE}" \
      "(DATABASE_URL con formato inesperado: '${EXISTING_URL}')." >&2
    echo "Revisar el archivo manualmente, o eliminarlo para que el instalador genere" \
      "credenciales nuevas de forma consistente." >&2
    exit 1
  fi
else
  DB_PASSWORD="$(openssl rand -hex 24)"
  WRITE_ENV=true
  echo "    ${ENV_FILE} no existe: se generan credenciales nuevas."
fi

echo "==> Sincronizando rol y base de datos PostgreSQL con la contraseña vigente"
# ALTER ROLE (no solo CREATE ROLE IF NOT EXISTS) es lo que hace esto idempotente de verdad:
# si el rol ya existia con otra contraseña (p. ej. porque se perdio .env), queda forzado a
# coincidir con DB_PASSWORD en vez de conservar un valor que ya no conocemos.
sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL
    DO \$\$
    BEGIN
      IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
      ELSE
        ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
      END IF;
    END
    \$\$;
    SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
EOSQL

echo "==> Verificando conectividad con las credenciales resueltas"
if ! PGPASSWORD="${DB_PASSWORD}" psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1;" >/dev/null; then
  echo "No se pudo conectar a PostgreSQL como '${DB_USER}' con la contraseña resuelta." >&2
  echo "Rol y credenciales quedaron desincronizados; abortando antes de escribir ${ENV_FILE}." >&2
  exit 1
fi

if [[ "${WRITE_ENV}" == true ]]; then
  echo "==> Generando ${ENV_FILE}"
  cat > "${ENV_FILE}" <<-EOF
	TONY_ENV=production
	LOG_LEVEL=INFO
	DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
	EOF
  chmod 600 "${ENV_FILE}"
else
  echo "==> ${ENV_FILE} sin cambios (credenciales ya consistentes con PostgreSQL)"
fi

echo "==> Preparando directorio de datos en runtime (var/)"
mkdir -p "${INSTALL_DIR}/var"

chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"

echo "==> Aplicando migraciones (alembic upgrade head)"
sudo -u "${SERVICE_USER}" bash -c "cd '${INSTALL_DIR}' && '${INSTALL_DIR}/.venv/bin/python' -m alembic upgrade head"

echo "==> Instalando unidad systemd"
install -m 644 "${INSTALL_DIR}/systemd/units/tony.service" /etc/systemd/system/tony.service
systemctl daemon-reload
systemctl enable tony.service

echo "==> Listo. Iniciar con: systemctl start tony.service"
echo "==> Ver logs con:       journalctl -u tony.service -f"
