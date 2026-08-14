# integrity

**Estado:** carpeta reservada, sin implementacion todavia.

**Responsabilidad prevista:** Verificacion de integridad del log de auditoria (deteccion de alteraciones, encadenamiento de checksums).

**Cuando se implementa:** v0.3 S18/Fase 11 (v0.1).

**Gap que cierra (importante, revisado en la review de v0.0.1):** hoy `audit_events` es
append-only solo a nivel `AuditEventRepository`/API (`database/repositories/audit_repository.py`
no expone `update()`/`delete()`). El rol de PostgreSQL con el que corre TONY es owner de la
tabla y conserva privilegios `UPDATE`/`DELETE` a nivel de motor; nada en el esquema actual se
lo impide. Esta carpeta es donde se cierra esa brecha, con al menos una de estas dos vias (o
ambas): revocar `UPDATE`/`DELETE` al rol de runtime (separando un rol de escritura restringido
del rol de migraciones), y/o encadenar checksums por evento para poder detectar alteraciones
hechas por fuera de la aplicacion. No implementar ninguna mientras el hito de origen (v0.0.1)
este activo evita mezclar hardening con la base minima que ese hito verifica.

Ver la fuente de verdad de arquitectura en `docs/architecture/` (v0.1, v0.2, v0.3) antes de
agregar codigo aqui. Cualquier decision que la contradiga debe presentarse como cambio de
arquitectura (nuevo ADR en `docs/adr/`), no implementarse directamente.
