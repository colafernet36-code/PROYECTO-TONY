#!/usr/bin/env bash
# Instala TONY v0.0.1 (Core Bootstrap) en Kali/Debian/Ubuntu (v0.2 S1: "Plataforma: PC
# dual-boot, primera implementacion en Kali Linux"; v0.3 S19 pasos 1-6).
#
# Revisar antes de ejecutar en una maquina real. Pensado para correr como root o con sudo.
#
# Uso:
#   sudo ./scripts/install/install_kali.sh [/ruta/de/instalacion]
#
# Por defecto instala en /opt/tony. No sobreescribe un .env existente.

set -euo pipefail

INSTALL_DIR="${1:-/opt/tony}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICE_USER="tony"
DB_NAME="tony"
DB_USER="tony"

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

echo "==> Configurando rol y base de datos PostgreSQL (idempotente)"
DB_PASSWORD="$(openssl rand -hex 24)"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<-EOSQL
    DO \$\$
    BEGIN
      IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
      END IF;
    END
    \$\$;
    SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
EOSQL

if [[ ! -f "${INSTALL_DIR}/.env" ]]; then
  echo "==> Generando ${INSTALL_DIR}/.env"
  cat > "${INSTALL_DIR}/.env" <<-EOF
	TONY_ENV=production
	LOG_LEVEL=INFO
	DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
	EOF
  chmod 600 "${INSTALL_DIR}/.env"
else
  echo "==> ${INSTALL_DIR}/.env ya existe, no se sobreescribe"
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
