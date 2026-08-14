#!/usr/bin/env bash
# Diagnostico rapido de TONY en Linux: PostgreSQL, servicio systemd y ultimo system.tony_ready.
# Uso: ./scripts/diagnostics/health_check.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_DIR}"

status=0

echo "== PostgreSQL =="
if command -v pg_lsclusters >/dev/null 2>&1; then
  pg_lsclusters || true
fi
if command -v pg_isready >/dev/null 2>&1; then
  if pg_isready -q; then
    echo "pg_isready: OK"
  else
    echo "pg_isready: FALLA"
    status=1
  fi
fi

echo
echo "== Servicio systemd tony.service =="
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files tony.service >/dev/null 2>&1; then
  systemctl status tony.service --no-pager || status=1
else
  echo "tony.service no esta instalado en este host (ver scripts/install/install_kali.sh)"
fi

echo
echo "== Ultimos audit_events (categoria boot) =="
if [[ -f .venv/bin/python ]]; then
  PY=.venv/bin/python
else
  PY=python3
fi

"${PY}" - <<'PYEOF' || status=1
from sqlalchemy import select

from database.models.audit_event import AuditEventORM
from database.session import make_engine, make_session_factory

engine = make_engine()
Session = make_session_factory(engine)
with Session() as session:
    rows = session.scalars(
        select(AuditEventORM)
        .where(AuditEventORM.category == "boot")
        .order_by(AuditEventORM.created_at.desc())
        .limit(5)
    ).all()
    if not rows:
        print("Sin eventos de boot todavia.")
    for row in rows:
        print(f"{row.created_at}  {row.actor}  {row.description}")
PYEOF

exit "${status}"
