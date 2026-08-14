# Seguridad

**Estado:** reservado. El threat model formal figura como pendiente explicito en v0.2 S14 y v0.3.

**Responsabilidad prevista:** threat model completo, matriz de acciones por RiskLevel,
diseno del AuthorizationGrant (nonce, expiracion, firma), y politica de secretos/backups/cifrado.

**Cuando se implementa:** en paralelo a `security/policy_engine` (paso 7) y se cierra antes del
paso 14 (Authorization Service + cliente iPhone/Face ID).
