# PROYECTO TONY — Especificación Técnica y Estructura de Repositorio

**Versión 0.3 — Baseline previo a implementación**

Esta versión consolida la arquitectura acordada desde la visión inicial hasta el punto
inmediatamente anterior a escribir el código real. Define plataforma, lenguajes,
responsabilidades, contratos, flujo de órdenes, seguridad, memoria, domótica, UI, servicios y
estructura completa inicial del repositorio.

> **Regla de desarrollo**: implementar un hito pequeño dentro de esta arquitectura, probarlo en
> Kali Linux, corregir inmediatamente, volver a probar y avanzar sólo cuando el hito esté
> estable.
>
> **Este es el documento de arquitectura vigente del repositorio.** v0.1 y v0.2 se conservan en
> `especificacion-v0.1.md` y `especificacion-v0.2.md` como historial de decisiones.

## 1. Objetivo definitivo de TONY

TONY será un asistente personal inteligente local-first, modular y extensible. Debe conversar
naturalmente, mantener memoria persistente autorizada, colaborar en proyectos complejos,
investigar, programar, gestionar agenda y rutinas, operar la computadora, controlar
dispositivos del hogar y coordinar diferentes modelos de IA manteniendo una identidad única.

La arquitectura evita convertir al modelo de lenguaje en un proceso con privilegios
permanentes. El Core interpreta y coordina; Policy Engine autoriza; agentes especializados
ejecutan; Audit Service registra.

## 2. Plataforma base

- **Equipo**: computadora dual-boot.
- **Desarrollo principal**: Kali Linux.
- **Segunda plataforma**: Windows, mediante agente equivalente en una fase posterior.
- **Arranque**: la PC podrá encender/despertar mediante RTC/UEFI/BIOS o mecanismo soportado por
  hardware. Una vez iniciado Linux, systemd inicia TONY.
- **Modo de operación**: servicios persistentes y componentes desacoplados; la interfaz puede
  ocultarse sin detener el Core.

## 3. Stack tecnológico

| Tecnología | Uso principal |
|---|---|
| Python 3 | TONY Core, orquestación, AI Router, memoria, voz, research, tools, scheduler, API |
| Rust | Privileged Agent, componentes sensibles del Policy Engine y ejecución privilegiada |
| TypeScript | Interfaz moderna y clientes visuales; futura interfaz web/móvil cuando corresponda |
| PostgreSQL | Persistencia principal: identidad, memoria, proyectos, acciones, auditoría, automatizaciones |
| pgvector | Búsqueda semántica y recuperación de recuerdos/contexto |
| SQL | Esquemas, consultas, migraciones y consistencia de datos |
| Bash | Instalación, diagnóstico, backup y mantenimiento Linux; no será el cerebro |
| systemd | Inicio automático, ciclo de vida y supervisión de servicios Linux |
| Home Assistant | Gateway/capa de abstracción para domótica local |

## 4. Arquitectura del cerebro y circulación de una orden

```text
VOICE/TEXT
   |
Wake Word / Input
   |
Speaker Verification (cuando corresponda)
   |
STT
   |
TONY CORE
   |-- Session Manager
   |-- Context Engine
   |-- Memory Retrieval
   |-- Intent Engine
   |
ACTION estructurada
   |
POLICY ENGINE
   |-----------------------------|
NORMAL / permitida            CRITICAL
   |                              |
TOOL ROUTER              Authorization Service
   |                              |
AGENT                    iPhone confiable -> Face ID
   |                              |
EXECUTE                  AuthorizationGrant
   |                              |
RESULT <------------------- validacion
   |
AUDIT + EVENT BUS
   |
TONY CORE -> TTS/UI
```

El texto generado por un LLM nunca se considera por sí mismo una autorización. Toda ejecución
se representa primero como `Action`/`ToolCall` estructurada y pasa por la política
correspondiente.

## 5. Contratos compartidos

Implementados en `contracts/` (lenguaje común entre Python, Rust y TypeScript):

- **`Action`**: solicitud universal normalizada: `action_id`, `session_id`, `user_id`,
  `source`, `intent`, `parameters`, `target`, `risk_level`, `status` y timestamps.
- **`ToolCall`**: operación concreta para un agente: `tool`, `operation`, `arguments`,
  `working_directory`, `timeout` y `execution_policy`.
- **`ToolResult`**: resultado estructurado: success/error, output permitido, `exit_code`,
  `duration` y referencias de auditoría.
- **`RiskLevel`**: `LOW`, `NORMAL`, `IMPORTANT`, `CRITICAL`.
- **`AuthorizationRequest`**: solicitud ligada a `action_id` y `trusted_device`.
- **`AuthorizationGrant`**: grant firmado, de un solo uso, con `action_id`, `device_id`,
  `nonce`, `issued_at`, `expires_at`, `signature` y `consumed`.
- **`AuditEvent`**: evento inmutable/orientado a append para trazabilidad.
- **`MemoryItem`**: recuerdo estructurado con fuente, importancia, confianza, relaciones y
  embedding cuando aplique.
- **`AIRequest`/`AIResponse`**: contrato neutral para que TONY no dependa de un proveedor.
- **`SystemEvent`**: evento publicado en Event Bus.
- **`ErrorResponse`**: error normalizado entre módulos.

## 6. Estados de Action

```text
CREATED
   |
VALIDATING
   |
CLASSIFIED
   |----------------------|
NORMAL/IMPORTANT       CRITICAL
   |                       |
   |                 WAITING_AUTH
   |                       |
   |                  AUTHORIZED
   |______________________|
              |
          EXECUTING
          /       \
    COMPLETED   FAILED

Estados terminales adicionales:
REJECTED / CANCELLED / EXPIRED
```

Una acción crítica que estaba esperando autorización no se reanuda automáticamente tras
reiniciar TONY. Debe generarse una nueva autorización.

## 7. Seguridad y Face ID

Para operaciones CRITICAL se exige speaker verification más una aprobación desde el iPhone
registrado como trusted device. TONY no almacena la cara ni la plantilla biométrica. Face ID
es validado por iOS/Apple; el cliente confiable devuelve una prueba criptográfica.

- Una acción crítica = una autenticación Face ID.
- `AuthorizationGrant` ligado a un único `action_id`.
- Nonce único, expiración corta, firma verificable y estado `consumed`.
- Un grant utilizado no puede reutilizarse.
- Una segunda acción crítica requiere un nuevo Face ID.
- No puede existir bypass de debug, LLM, terminal o UI para CRITICAL.
- Secrets Manager almacena credenciales/tokens fuera del código y fuera de texto plano.
- Emergency Stop, cancelación, sandbox/dry-run, mínimo privilegio interno y recuperación segura
  forman parte del sistema.

## 8. PostgreSQL — dominios y esquema inicial

- **Identidad**: `users`, `trusted_devices`, `speaker_profiles`.
- **Conversación**: `sessions`, `conversations`, `messages`.
- **Memoria**: `memories`, `memory_links`, `memory_embeddings`.
- **Proyectos**: `projects`, `project_artifacts`, `project_context`.
- **Ejecución**: `actions`, `tool_calls`, `tool_results`.
- **Seguridad**: `permissions`, `authorization_grants`, `security_events`.
- **Auditoría**: `audit_events`.
- **IA**: `ai_requests`, `ai_responses`, `model_metrics`.
- **Automatización**: `automation_rules`, `schedules`, `routines`, `routine_steps`,
  `routine_runs`, `scheduled_tasks`.
- **Domótica**: `smart_home_devices`, `device_capabilities`, `device_states`, `device_groups`,
  `scenes`.
- **Sistema**: `system_devices`, `system_state`, `service_health`, `notifications`.

> **Nota de implementación (v0.0.1)**: sólo `audit_events` está migrado hoy (ver
> `database/migrations/versions/0001_audit_events.py`). El resto de los dominios se agrega en
> el paso del "Orden oficial de implementación" (§19) que los necesita — ver el estado real en
> `docs/adr/0001-bootstrap-v0.0.1.md`.

### 8.1 Memoria semántica

PostgreSQL + pgvector permitirá combinar filtros SQL con similitud semántica. Ante preguntas
como "te acordás del problema de hace seis meses con el módulo de memoria", Memory Retrieval
buscará recuerdos relacionados por significado, proyecto, fecha, importancia y enlaces, y sólo
entregará al modelo el contexto relevante.

Audit, logs, metrics y memory permanecen separados: un log técnico no es automáticamente un
recuerdo y un recuerdo editable no debe poder reescribir el historial de auditoría.

## 9. Event Bus

Eventos iniciales: `voice.wake_detected`, `voice.transcription_ready`, `voice.speaking`,
`action.created`, `action.authorized`, `action.rejected`, `action.executing`,
`action.completed`, `action.failed`, `security.authorization_required`,
`security.authorization_granted`, `memory.created`, `memory.recalled`, `ai.requested`,
`ai.completed`, `system.tony_ready`, `system.degraded`.

La UI y otros componentes observan eventos; no deben controlar directamente la lógica central.

Implementado en `core/event_bus/` como bus pub/sub en proceso (`contracts/events.py` define
`EventType` y `SystemEvent`).

## 10. AI Router

TONY mantiene identidad única y selecciona modelos mediante AI Router. Proveedores previstos:
OpenAI/ChatGPT, Anthropic/Claude, Google/Gemini y modelos locales/futuros. No se consultan
todos simultáneamente por defecto.

Criterios: tipo de tarea, contexto, privacidad, necesidad de tools, calidad observada, costo,
latencia, disponibilidad y fallback. Preferencias iniciales pueden favorecer Claude en
programación, ChatGPT en razonamiento/información/lógica y Gemini en ciertas tareas
multimedia, pero son configurables.

## 11. Voz

```text
Wake Word ("Tony")
      |
Speaker ID
      |
Speech-to-Text
      |
TONY Core
      |
Text-to-Speech
      |
Altavoz / dispositivos de salida
```

Wake word, speaker verification, STT y TTS son subsistemas independientes. Los motores
concretos se elegirán mediante benchmarks de calidad, latencia, naturalidad, privacidad,
mantenimiento, licencia y compatibilidad Linux.

## 12. Terminal y herramientas Linux

Terminal/Tool Agent convierte lenguaje natural en `ToolCall` estructurada. Podrá administrar
archivos, carpetas, procesos, entornos de desarrollo, diagnóstico y herramientas de
ciberseguridad en sistemas propios o expresamente autorizados. El Core no contendrá una lista
rígida de cientos de comandos.

```text
Natural language
   -> Intent Parser
   -> Tool Registry / Adapter
   -> Structured ToolCall
   -> Risk Classifier
   -> Policy Engine
   -> Agent execution
   -> ToolResult
   -> Audit
```

Cada adapter declara operaciones, parámetros, permisos, riesgos, timeouts y forma de
interpretar resultados. Las acciones sensibles pueden ejecutarse primero en dry-run/sandbox
cuando corresponda.

## 13. Domótica

Home Assistant será la capa de abstracción. Se priorizan integraciones locales mediante
Matter/Thread, Zigbee y APIs locales. Referencias iniciales: Philips Hue + Hue Bridge para
iluminación y Aqara U200/Matter over Thread como candidata para cerradura, conservando siempre
un método físico/manual independiente.

`SmartHomeAgent` utilizará `DeviceRegistry`, `SmartHomeAction` y `DeviceState`. Cada
dispositivo posee identificador, habitación, nombre, capacidades, estado y conectividad.

```yaml
kitchen.main_light:
  type: LIGHT
  room: kitchen
  capabilities:
    - power
    - brightness
    - color_temperature
    - rgb
  state:
    power: ON
    brightness: 30
```

El riesgo pertenece a la operación: ajustar una luz al 30% puede ser NORMAL; desbloquear una
cerradura es CRITICAL y exige voz + Face ID + grant único. Se soportarán grupos y escenas.

## 14. Scheduler, rutinas y briefing

```text
06:00
  -> PC wake/boot
  -> Kali
  -> systemd
  -> TONY health/security
  -> PostgreSQL + Memory
  -> Smart Home Agent
       -> luces habitacion 100%
  -> Context Engine
       hora / fecha / clima
       calendario / recordatorios
  -> TTS
       -> "Buenos dias, señor..."
```

La rutina no se codificará como comportamiento fijo. Scheduler/Routine Engine almacenará
schedules, pasos, ejecuciones y estados para permitir editar horarios y acciones.

## 15. UI moderna

TypeScript implementará una interfaz desacoplada del Core. Concepto inicial: esfera/objeto
central animado que cambia según `idle`, `listening`, `transcribing`, `thinking`, `speaking`,
`authorization_required` y `error`. La UI mostrará conversación, actividad, servicios,
autorizaciones pendientes y controles minimizar/ocultar/salir.

Luces ambientales u otras superficies visuales podrán reaccionar a eventos de TONY mediante
Smart Home/Visual Gateway.

## 16. Estructura completa inicial del repositorio

```text
TONY/
|-- README.md
|-- pyproject.toml
|-- .gitignore
|-- .env.example
|-- docker-compose.yml
|
|-- contracts/
|   |-- action/
|   |-- tools/
|   |-- authorization/
|   |-- memory/
|   |-- ai/
|   |-- events/
|   `-- errors/
|
|-- core/
|   |-- orchestrator/
|   |-- sessions/
|   |-- context/
|   |-- intent/
|   |-- reasoning/
|   |-- tool_router/
|   |-- memory_gateway/
|   |-- event_bus/
|   `-- bootstrap/
|
|-- ai/
|   |-- router/
|   |-- providers/
|   |   |-- openai/
|   |   |-- anthropic/
|   |   `-- google/
|   |-- local/
|   |-- prompts/
|   `-- evaluation/
|
|-- memory/
|   |-- short_term/
|   |-- long_term/
|   |-- retrieval/
|   |-- embeddings/
|   |-- consolidation/
|   `-- policies/
|
|-- voice/
|   |-- wake_word/
|   |-- speaker_id/
|   |-- stt/
|   |-- tts/
|   `-- audio_io/
|
|-- security/
|   |-- policy_engine/
|   |-- risk/
|   |-- authentication/
|   |-- authorization/
|   |-- trusted_devices/
|   |-- secrets/
|   |-- sandbox/
|   `-- emergency_stop/
|
|-- agents/
|   |-- linux/
|   |-- terminal/
|   |-- filesystem/
|   |-- browser/
|   |-- projects/
|   |-- research/
|   |-- calendar/
|   |-- notifications/
|   `-- smart_home/
|
|-- audit/
|   |-- service/
|   |-- writers/
|   `-- integrity/
|
|-- database/
|   |-- migrations/
|   |-- models/
|   |-- repositories/
|   |-- vector/
|   `-- seeds/
|
|-- automation/
|   |-- scheduler/
|   |-- routines/
|   `-- rules/
|
|-- observability/
|   |-- logging/
|   |-- metrics/
|   `-- health/
|
|-- backup/
|   |-- backup_service/
|   `-- recovery/
|
|-- api/
|   |-- internal/
|   |-- websocket/
|   `-- schemas/
|
|-- ui/
|   |-- desktop/
|   |-- components/
|   |-- state/
|   `-- animations/
|
|-- mobile/
|   `-- ios_authorization_client/
|
|-- privileged-agent/
|   |-- src/
|   |-- tests/
|   `-- Cargo.toml
|
|-- config/
|   |-- environments/
|   |-- policies/
|   `-- defaults/
|
|-- scripts/
|   |-- install/
|   |-- update/
|   |-- backup/
|   `-- diagnostics/
|
|-- systemd/
|   `-- units/
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- security/
|   `-- end_to_end/
|
`-- docs/
    |-- architecture/
    |-- adr/
    |-- security/
    |-- api/
    `-- operations/
```

> Esta es la estructura vigente del repositorio real. Cada carpeta no implementada todavía
> contiene un `README.md` con su responsabilidad prevista y la fase en la que se implementa
> (ver §17 y `docs/adr/0001-bootstrap-v0.0.1.md`).

## 17. Responsabilidad de carpetas clave

- **`contracts/`**: lenguaje común entre Python, Rust, TypeScript y futuros clientes.
- **`core/`**: cerebro/orquestador; no ejecuta directamente operaciones privilegiadas.
- **`ai/`**: proveedores intercambiables, routing y evaluación.
- **`memory/`**: recuperación, embeddings, consolidación y reglas de memoria.
- **`security/`**: riesgo, permisos, autenticación, grants, secretos y parada de emergencia.
- **`agents/`**: capacidades concretas sobre el mundo: Linux, terminal, archivos, research,
  calendario y hogar.
- **`audit/`**: trazabilidad independiente de memoria conversacional.
- **`database/`**: modelos, migraciones y acceso persistente.
- **`automation/`**: scheduler y rutinas como la secuencia matutina.
- **`observability/`**: salud, logs y métricas.
- **`mobile/ios_authorization_client/`**: cliente confiable que recibe `AuthorizationRequest`,
  invoca autenticación soportada por iOS y devuelve grant verificable.
- **`privileged-agent/`**: binario Rust con superficie mínima para operaciones que realmente
  requieren privilegios.
- **`docs/adr/`**: Architecture Decision Records para documentar cambios importantes.

## 18. Servicios operativos adicionales

- **Notification Engine**: voz, UI, iPhone y futuros canales.
- **Health Monitor**: `ONLINE`, `DEGRADED`, `OFFLINE` por servicio/dispositivo.
- **Backup/Recovery**: copias cifradas de configuración, memoria y PostgreSQL.
- **Update Manager**: actualizaciones controladas y probadas antes de componentes críticos.
- **Network policy**: diferenciar local, LAN e Internet y no exponer servicios internos
  innecesariamente.
- **Cancellation**: "Tony, cancela" detiene acciones pendientes cuando sea seguro.
- **Emergency Stop**: mecanismo independiente para detener agentes/automatizaciones.
- **Observability**: Audit, logs, metrics y memory separados.

## 19. Orden oficial de implementación

1. Crear `TONY/` y archivos raíz.
2. Preparar entorno Python y control de versiones.
3. Crear shared contracts.
4. Implementar bootstrap de TONY Core y Event Bus.
5. Instalar/configurar PostgreSQL y primeras migraciones.
6. Implementar Audit Service.
7. Implementar Policy Engine inicial y `RiskLevel`.
8. Implementar Terminal Agent en dry-run.
9. Integrar primer proveedor mediante AI Router.
10. Agregar conversación básica.
11. Agregar memoria persistente y luego pgvector.
12. Agregar STT/TTS; luego wake word y speaker verification.
13. Construir UI inicial.
14. Crear trusted-device/Authorization Service y cliente iPhone/Face ID.
15. Activar ejecución privilegiada Rust con políticas.
16. Agregar calendario, scheduler, notificaciones y rutinas.
17. Agregar Home Assistant, DeviceRegistry, luces y después cerraduras.
18. Expandir Tool Registry y agentes.
19. Hardening, backups, recovery, pruebas de seguridad y Windows agent.

> **Estado real (ver `docs/adr/0001-bootstrap-v0.0.1.md`)**: pasos 1–6 completos y verificados
> (hito v0.0.1). Paso 7 (Policy Engine) es el siguiente hito a abrir.

## 20. Primer hito programable

```text
Kali Linux
   |
systemd
   |
TONY Core Bootstrap
   |
PostgreSQL
   |
Event Bus
   |
Audit Service
   |
publish: system.tony_ready
```

No se avanza al siguiente hito hasta verificar este recorrido. Esta será la primera versión
ejecutable real de TONY.

> **Implementado.** Ver `core/bootstrap/bootstrap.py`, entry point `tony` (definido en
> `pyproject.toml`), y `systemd/units/tony.service`.

## 21. Filosofía permanente de desarrollo

- Construir sobre la arquitectura definitiva, no prototipos desechables.
- Explicar cada paso: qué, por qué, nombre, ruta, código/comando y forma de comprobarlo.
- Implementar -> probar -> corregir -> volver a probar -> estabilizar -> avanzar.
- Las capturas de Kali pueden utilizarse para verificar el estado real antes de continuar.
- Usar otras IAs cuando aporten velocidad o revisión, entregándoles esta especificación como
  fuente de verdad.
- Priorizar velocidad de desarrollo sin sacrificar seguridad, mantenibilidad ni trazabilidad.
- Versionar cambios de arquitectura y agregar nuevas ideas en la sección correspondiente.

## 22. Estado de cierre v0.3

La arquitectura inicial queda suficientemente especificada para comenzar la implementación. A
partir de este punto, las nuevas decisiones surgirán principalmente de la programación y las
pruebas. El repositorio real se construirá siguiendo la estructura de esta versión y cualquier
cambio estructural relevante deberá documentarse.

**Siguiente paso:** TONY v0.0.1 — Core Bootstrap en Kali Linux. *(completado — ver
`docs/adr/0001-bootstrap-v0.0.1.md`)*
