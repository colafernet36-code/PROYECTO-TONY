# PROYECTO TONY — Especificación Maestra de Arquitectura del Sistema

**Versión 0.2 — Arquitectura técnica inicial**

Objetivo: convertir la visión v0.1 en una base técnica suficientemente precisa para comenzar la
estructura real del software sin cerrar prematuramente componentes que todavía deben evaluarse.

Fuente de verdad versionada del Proyecto TONY. Las decisiones futuras deben conservar
compatibilidad con seguridad, modularidad, trazabilidad y control humano.

## 1. Decisiones cerradas en v0.2

- **Plataforma**: PC dual-boot. Primera implementación y desarrollo en Kali Linux;
  posteriormente agente equivalente para Windows.
- **Inicio automático**: TONY se ejecutará como servicio al arrancar. En Linux se utilizará
  systemd.
- **Local-first**: identidad, configuración, políticas, memoria privada y control pertenecen a
  TONY; los modelos externos son motores reemplazables.
- **Seguridad**: una acción CRITICAL nunca puede llegar al ejecutor sin autenticación reforzada.
- **Memoria**: PostgreSQL como base principal y pgvector previsto para recuperación semántica.
- **Auditoría**: movimientos importantes, autorizaciones, herramientas y resultados se
  guardarán mediante Audit Service.
- **IA**: AI Router configurable seleccionará proveedor/modelo según tarea, privacidad,
  capacidad, latencia y disponibilidad.
- **Terminal**: Terminal/Tool Agent traducirá instrucciones naturales a operaciones Linux
  autorizadas y auditadas.
- **Interfaz**: UI moderna con estados visuales dinámicos de escucha, pensamiento, habla,
  autorización, error y reposo.

## 2. Mapa de lenguajes y tecnologías

| Tecnología | Responsabilidad inicial | Razón |
|---|---|---|
| Python 3 | Core, AI Router, memoria, voz, research, tool routing, automatización | Ecosistema IA, integración y velocidad de desarrollo |
| Rust | Policy Engine sensible, privileged agent, seguridad | Robustez, seguridad de memoria y superficie reducida |
| TypeScript | Interfaz gráfica/panel y futuras interfaces web | UI moderna, tipado y ecosistema |
| SQL | Memoria, auditoría, permisos, proyectos y dispositivos | Consistencia y trazabilidad |
| Bash | Instalación, diagnóstico, actualización y mantenimiento Linux | Integración nativa; no será el cerebro |

## 3. Arquitectura del cerebro

TONY no será un único proceso con privilegios irrestrictos. La capacidad global se construirá
mediante componentes especializados. El Core razona y coordina; Policy Engine decide; los
agentes ejecutan sólo las capacidades que les corresponden.

```text
USUARIO
  |
VOICE GATEWAY -> TONY CORE -> CONTEXT / MEMORY
              |
      +-------+-------+
      |               |
  AI ROUTER      TOOL ROUTER
                       |
                 POLICY ENGINE
                  /         \
             NORMAL       CRITICAL
               |               |
            ejecutar    voz verificada
                              |
                       iPhone confiable
                              |
                           Face ID
                              |
                       grant autorizado
                              |
                           ejecutar
                              |
                            AUDIT
```

## 4. Política de acciones

- **Normal**: una vez interpretada y permitida por las reglas vigentes, puede ejecutarse sin
  segundo factor.
- **Critical**: reconocimiento del hablante + aprobación desde el iPhone registrado mediante la
  autenticación biométrica soportada por el dispositivo. TONY no almacena la plantilla de
  Face ID.
- **Invariante**: no existirá ruta alternativa, modo debug ni instrucción de modelo que permita
  ejecutar una acción CRITICAL sin un `AuthorizationGrant` válido.

## 5. Memoria y PostgreSQL

La memoria permitirá consultas exactas y recuperación semántica. TONY podrá relacionar
preguntas actuales con conversaciones, decisiones y proyectos de meses o años atrás aunque no
se recuerde la frase exacta.

**Entidades iniciales**: `users`, `trusted_devices`, `memories`, `memory_links`,
`conversations`, `messages`, `projects`, `project_artifacts`, `tasks`, `preferences`,
`automation_rules`, `permissions`, `authorizations`, `ai_requests`, `tool_calls`,
`audit_events`, `security_events`.

`audit_events` tendrá política distinta de la memoria conversacional: su función es
trazabilidad y detección de alteraciones.

## 6. AI Router

TONY mantendrá una identidad única aunque utilice diferentes proveedores. Las preferencias
iniciales por programación, razonamiento, investigación o multimedia serán configurables y se
ajustarán según evaluaciones.

```text
TASK -> AI ROUTER
          |-- OpenAI / modelos disponibles
          |-- Anthropic / modelos disponibles
          |-- Google / modelos disponibles
          `-- modelos locales o futuros
```

Criterios: tarea, contexto, privacidad, tools, calidad observada, costo, latencia,
disponibilidad y fallback.

## 7. Terminal / Tool Agent para Kali Linux

TONY recibirá instrucciones naturales y podrá convertirlas en operaciones de terminal:
administración de archivos, procesos, diagnóstico, desarrollo y herramientas de ciberseguridad
sobre sistemas propios o expresamente autorizados.

El texto producido por un modelo no será tratado automáticamente como una orden confiable. El
agente generará una `ToolCall` estructurada, resolverá parámetros, clasificará riesgo, pasará
por Policy Engine y registrará comando, autorización, resultado y código de salida.

```text
lenguaje natural
      |
INTENT PARSER
      |
STRUCTURED TOOL CALL
      |
RISK CLASSIFIER
      |
POLICY ENGINE
      |
AUTHORIZED EXECUTION
      |
Linux terminal
      |
result + audit
```

Las herramientas Linux y de seguridad se incorporarán mediante un registro extensible de
adapters con esquemas de parámetros, permisos y reglas. Esto evita codificar cientos de
comandos directamente en el Core.

## 8. Voice Gateway

- **Wake word**: activación por el nombre configurado, inicialmente "Tony".
- **Speaker verification**: identifica al hablante autorizado; no reemplaza el segundo factor
  de acciones críticas.
- **STT**: conversión de voz a texto con baja latencia.
- **TTS**: voz natural y expresiva; motor definitivo tras pruebas comparativas.
- **Estados**: `idle`, `listening`, `transcribing`, `thinking`, `speaking`,
  `authorization_required` y `error`.

## 9. Interfaz visual

La primera interfaz no será una terminal ni una ventana básica. TypeScript soportará una capa
visual moderna desacoplada del Core. Concepto inicial: esfera u objeto central animado que
reacciona al estado de TONY.

La UI mostrará conversación, actividad, autorizaciones pendientes, estado de servicios y
controles para minimizar, ocultar o salir. La iluminación ambiental y futuras interfaces 3D se
tratarán como dispositivos conectados, no como lógica fija de la UI.

## 10. Estructura inicial del repositorio (v0.2)

```text
TONY/
|-- core/
|   |-- orchestrator/
|   |-- context/
|   |-- reasoning/
|   `-- events/
|-- ai/
|   |-- router/
|   |-- providers/
|   `-- local/
|-- memory/
|   |-- long_term/
|   |-- short_term/
|   |-- embeddings/
|   `-- retrieval/
|-- voice/
|   |-- wake_word/
|   |-- speaker_id/
|   |-- stt/
|   `-- tts/
|-- security/
|   |-- policy_engine/
|   |-- authentication/
|   |-- trusted_devices/
|   `-- authorization/
|-- agents/
|   |-- linux/
|   |-- terminal/
|   |-- filesystem/
|   |-- browser/
|   |-- projects/
|   |-- calendar/
|   `-- smart_home/
|-- audit/
|-- database/
|   |-- migrations/
|   |-- models/
|   `-- repositories/
|-- api/
|-- ui/
|-- privileged-agent/   # Rust
|-- scripts/
|-- tests/
|-- config/
`-- docs/
```

> Superada por la estructura completa de `especificacion-v0.3.md` §16, que es la vigente en el
> repositorio real.

## 11. Flujo de arranque Linux

```text
Kali Linux boot
      |
   systemd
      |
TONY bootstrap
      |
health + security checks
      |
database + memory
      |
voice + AI router + tools
      |
automation context
      |
  TONY READY
```

Un fallo en cualquier componente no debe otorgar permisos adicionales ni omitir autenticación.

## 12. Política para bibliotecas y motores

v0.2 fija responsabilidades, no todas las versiones concretas. Wake word, speaker
verification, STT, TTS, embeddings, drivers, runtime de UI y SDKs de IA se seleccionarán
mediante pruebas reproducibles.

Criterios: calidad, latencia, privacidad/localidad, mantenimiento, licencia, seguridad,
compatibilidad Linux, reemplazabilidad y costo operativo.

## 13. Orden de implementación (v0.2)

1. Crear el repositorio y estructura de paquetes.
2. Definir contratos internos: `Action`, `ToolCall`, `RiskLevel`, `AuthorizationGrant`,
   `AuditEvent`, `MemoryItem` y `AIRequest`.
3. Implementar TONY Core mínimo y sistema de eventos.
4. Levantar PostgreSQL y primeras migraciones.
5. Implementar Audit Service desde el comienzo.
6. Crear Policy Engine inicial y simulador de autorizaciones.
7. Crear Terminal Agent primero en dry-run y después habilitar ejecución según políticas.
8. Integrar el primer proveedor detrás de AI Router.
9. Integrar STT/TTS y luego wake word/speaker verification.
10. Construir la primera UI moderna.
11. Agregar dispositivo confiable y segundo factor.
12. Expandir tools, memoria semántica, calendario, research y smart home.

> Reemplazado por el "Orden oficial de implementación" de v0.3 §19 (más detallado, 19 pasos).

## 14. Pendientes para v0.3 (según v0.2)

- Contratos y modelos de datos exactos.
- Esquema SQL inicial y estrategia pgvector.
- Event bus/protocolo interno definitivo.
- Framework exacto de UI de escritorio.
- Benchmark y selección de STT, TTS, wake word y speaker verification.
- Diseño criptográfico del `AuthorizationGrant` del iPhone.
- Threat model formal y matriz completa de acciones.
- Sandbox y rollback para Terminal/Filesystem Agent.
- Primer registro de tools Linux y proceso para agregar adapters.
- Configuración, secretos y entornos dev/test/prod.

Estado al cierre de v0.2: arquitectura técnica inicial aprobada como base para comenzar el
repositorio. v0.3 transformará estos bloques en contratos, esquemas y componentes
programables.
