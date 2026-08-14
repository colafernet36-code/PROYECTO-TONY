# privileged-agent (Rust)

**Estado:** reservado, sin implementacion todavia.

**Responsabilidad prevista:** binario Rust de superficie minima que ejecuta unicamente las
operaciones que realmente requieren privilegios elevados en Linux, invocado por el Policy
Engine solo tras una autorizacion valida (nunca directamente por el LLM ni por texto libre).
Robustez y seguridad de memoria segun v0.2 S2.

**Cuando se implementa:** paso 15 del orden oficial de implementacion (v0.3 S19), junto con la
activacion completa del Policy Engine y RiskLevel CRITICAL.

Cuando se implemente, este directorio tendra su propio `Cargo.toml`, `src/` y `tests/`,
consistente con el resto del workspace pero versionado independientemente de `pyproject.toml`.
