# PROYECTO TONY — Especificación Maestra de Arquitectura del Sistema

**Versión 0.1 — Documento fundacional**

> Un asistente personal inteligente, local, modular, seguro y extensible, diseñado para
> conversar, recordar, investigar, colaborar, automatizar y controlar sistemas autorizados
> bajo supervisión humana.

Estado: arquitectura conceptual inicial. Este documento será la fuente de verdad versionada
del proyecto y deberá actualizarse cuando se aprueben nuevas capacidades o cambios de diseño.

## 1. Visión del proyecto

TONY será una plataforma de asistencia personal inteligente que acompañará a su propietario en
actividades cotidianas, aprendizaje, investigación y desarrollo de proyectos complejos. No se
concibe como un único modelo de IA, sino como un sistema que coordina modelos, memoria,
herramientas, dispositivos y servicios externos mediante una arquitectura común.

La experiencia buscada es continua: el usuario habla con TONY como con un asistente humano;
TONY comprende el contexto disponible, consulta sus memorias autorizadas, utiliza herramientas
cuando corresponda, explica lo que propone y ejecuta únicamente las acciones para las que posee
autorización.

## 2. Principios no negociables

| Principio | Definición |
|---|---|
| Control humano | El propietario conserva la autoridad final. Las acciones de alto impacto requieren autorización explícita y, cuando corresponda, autenticación reforzada. |
| Seguridad por diseño | Ningún componente recibe acceso total por defecto. Se aplica mínimo privilegio, separación de funciones, registros de auditoría y mecanismos de revocación. |
| Arquitectura modular | Voz, modelos de IA, memoria, automatización, hogar inteligente, calendario e interfaces deben poder sustituirse sin reconstruir todo el sistema. |
| Memoria controlable | TONY puede aprender información útil, pero el usuario debe poder consultar, corregir, exportar y eliminar recuerdos. |
| Trazabilidad | Las acciones importantes deben dejar un registro comprensible: qué se solicitó, qué componente actuó, con qué permisos y cuál fue el resultado. |
| Degradación segura | Si falla Internet, un modelo, un dispositivo o una autenticación, TONY debe reducir capacidades de forma segura en vez de improvisar. |

## 3. Capacidades objetivo

- **Conversación natural**: diálogo por voz y texto, personalidad coherente, contexto de sesión
  y capacidad de conversación informal.
- **Identidad y voz**: palabra de activación configurable (por ejemplo, "Tony"), respuesta de
  reconocimiento y síntesis de voz natural.
- **Memoria persistente**: recuerdos estructurados sobre preferencias, proyectos, decisiones,
  rutinas y conocimiento autorizado del entorno.
- **Colaboración intelectual**: programación, matemáticas, ciencias, escritura, planificación y
  resolución conjunta de problemas.
- **Investigación**: acceso controlado a Internet, priorizando documentación oficial,
  publicaciones académicas y fuentes verificables; las fuentes deben conservarse junto con las
  conclusiones importantes.
- **Gestión del día**: calendario, recordatorios, rutinas, briefing matutino, preparación de
  actividades y avisos contextuales.
- **Automatización del equipo**: abrir aplicaciones/proyectos, organizar archivos, ejecutar
  flujos y preparar entornos de trabajo dentro de políticas de permisos.
- **Hogar inteligente**: integración con plataformas y dispositivos autorizados para luces,
  sensores, audio y, con controles reforzados, dispositivos físicos sensibles.
- **Interfaz multimodal**: voz, texto, panel visual y futura visualización 3D/pseudo-holográfica
  sin acoplar el núcleo a una pantalla concreta.
- **Orquestación multi-IA**: posibilidad de usar distintos modelos especializados detrás de una
  identidad única de TONY.

## 4. Arquitectura lógica de alto nivel

- **Interfaz**: micrófonos, altavoces, escritorio, móvil, panel web y futuras interfaces 3D.
- **Identidad y autenticación**: wake word, reconocimiento del hablante como señal auxiliar,
  dispositivo confiable, autenticación fuerte y políticas por riesgo.
- **Orquestador TONY**: interpreta intención, reúne contexto, selecciona herramientas/modelos,
  solicita autorizaciones y coordina la ejecución.
- **Capa de IA**: uno o varios modelos de lenguaje/razonamiento, modelos de voz y herramientas
  especializadas.
- **Memoria y conocimiento**: memoria de corto plazo, memoria persistente, índice de proyectos,
  documentos y preferencias.
- **Herramientas**: sistema operativo, editor/código, navegador/investigación, calendario,
  notificaciones, domótica y otros conectores.
- **Seguridad y auditoría**: políticas, secretos, sandbox, registro de acciones, rollback cuando
  sea posible y botón de emergencia.

## 5. Modelo preliminar de permisos

TONY no tendrá un único permiso de "administrador total". Se propone un modelo de riesgo que
limite el daño ante errores, instrucciones ambiguas o compromiso de un componente.

| Nivel | Ejemplos | Autorización sugerida |
|---|---|---|
| 0 — Lectura segura | Consultar hora, clima, calendario, documentación pública | Sesión autenticada |
| 1 — Acción reversible | Abrir app, encender luz, crear borrador, mover archivo no crítico | Voz/sesión + política |
| 2 — Acción importante | Modificar proyecto, enviar información, cambiar automatización | Confirmación explícita |
| 3 — Acción crítica | Eliminar datos importantes, cerraduras, secretos, cambios administrativos | Confirmación fuerte en dispositivo confiable + biometría/PIN del dispositivo |

> **Nota de diseño**: Face ID debe utilizarse mediante mecanismos soportados por el
> dispositivo/plataforma. TONY no debe recibir ni almacenar la plantilla biométrica; solamente
> una prueba de que el dispositivo confiable autorizó la operación.

> Este esquema de 4 niveles (0–3) es el modelo *preliminar* de v0.1. La v0.3 (fuente de verdad
> vigente) lo reemplaza por `RiskLevel = LOW | NORMAL | IMPORTANT | CRITICAL` — ver
> `especificacion-v0.3.md` §5 y `contracts/action.py`.

## 6. Rutina de inicio objetivo

1. El equipo arranca según una programación soportada por hardware/firmware o por el entorno
   disponible.
2. El servicio central de TONY inicia y realiza comprobaciones de integridad, red, dispositivos
   y servicios.
3. Carga únicamente las credenciales necesarias desde un almacén seguro.
4. Obtiene contexto autorizado: fecha/hora, clima, calendario, recordatorios y estado del hogar.
5. Prepara el entorno previsto para ese momento.
6. Emite un briefing, por ejemplo: hora, fecha, descanso estimado si existe una fuente válida,
   clima, agenda y recordatorios.
7. Ejecuta automatizaciones permitidas, como iluminación, respetando las políticas configuradas.

## 7. Subsistemas que deberán especificarse

- TONY Core / Orchestrator
- Speech-to-Text, wake word y Text-to-Speech
- Gestión de identidad, dispositivos confiables y autenticación
- Policy Engine de permisos y riesgo
- Memory Service y base de conocimiento
- Project Workspace para código, documentos y proyectos
- Research Engine con citas/procedencia
- Calendar & Reminder Service
- Desktop Automation Agent
- Smart Home Gateway
- Notification Service
- Audit Log y observabilidad
- Secrets Manager
- Panel de administración y configuración
- Interfaz móvil para aprobaciones
- Interfaz visual/3D futura

## 8. Roadmap de construcción

- **Fase 0 — Especificación**: cerrar requisitos, amenazas, arquitectura, interfaces,
  tecnologías y criterios de aceptación.
- **Fase 1 — Núcleo conversacional**: orquestador, texto, voz, identidad de TONY, configuración
  y logging.
- **Fase 2 — Memoria**: memoria estructurada, búsqueda, corrección, borrado, privacidad y
  contexto de proyectos.
- **Fase 3 — Workspace**: lectura de repositorios, colaboración en código/documentos,
  herramientas con sandbox y control de cambios.
- **Fase 4 — Investigación**: búsqueda web/documental, fuentes, verificación, caché y
  trazabilidad.
- **Fase 5 — Agenda**: calendario, recordatorios, rutinas y briefing diario.
- **Fase 6 — Automatización PC**: agente local con permisos limitados, acciones reversibles,
  confirmaciones y recuperación.
- **Fase 7 — Hogar inteligente**: luces/audio/sensores primero; dispositivos físicos críticos
  sólo después de completar el modelo de seguridad.
- **Fase 8 — Autenticación reforzada**: aplicación/dispositivo confiable, aprobación biométrica
  y políticas de nivel 3.
- **Fase 9 — Multi-IA**: router de modelos, evaluación de calidad/costo/latencia y fallback.
- **Fase 10 — Interfaz avanzada**: panel multimodal, avatar/3D y compatibilidad con dispositivos
  de visualización futuros.
- **Fase 11 — Hardening**: pruebas de seguridad, aislamiento, backups, recuperación, monitoreo y
  pruebas de fallos.

## 9. Decisiones técnicas aún abiertas (en v0.1)

- Sistema operativo principal y requisitos de hardware.
- Lenguaje(s) del núcleo y de los agentes; Python es candidato fuerte para IA/orquestación, pero
  no queda fijado todavía.
- Base de datos relacional, vectorial y estrategia de archivos.
- Motor local vs. APIs externas para IA y voz.
- Protocolo de comunicación entre servicios.
- Plataforma de hogar inteligente y alcance real de integraciones con Alexa/dispositivos.
- Diseño de la aplicación móvil de autorización.
- Modelo exacto de amenazas y recuperación ante compromiso.
- Política de retención, cifrado y backups.
- Presupuesto de latencia, costo y disponibilidad.

> Todas estas quedaron cerradas o refinadas en v0.2/v0.3 — ver esos documentos.

## 10. Reglas para futuras IAs y colaboradores

- Este documento es la fuente de verdad. Una propuesta que contradiga una decisión aprobada
  debe presentarse como cambio de arquitectura, no implementarse silenciosamente.
- No otorgar privilegios administrativos globales para resolver rápidamente una integración.
- Toda función sensible debe especificar: entrada, salida, permisos, riesgos, autenticación,
  registro y estrategia de fallo.
- Toda dependencia externa debe justificar su necesidad, mantenimiento, licencia, seguridad y
  posibilidad de reemplazo.
- Las acciones sobre el mundo físico o datos críticos requieren criterios de aceptación y
  pruebas específicas.
- El código se versionará y revisará; las decisiones arquitectónicas importantes deberán quedar
  documentadas.

## 11. Próxima especificación

La siguiente revisión (v0.2) deberá convertir esta visión en requisitos verificables y cerrar la
arquitectura tecnológica inicial. En particular: sistema operativo objetivo, hardware,
lenguajes, estructura de repositorios, procesos/servicios, base de datos, protocolo interno,
motor de voz, estrategia de modelos de IA, almacenamiento de secretos, niveles de permisos y
primer diagrama de despliegue.

> Documento vivo: las nuevas ideas se incorporarán en la sección correspondiente y se
> registrarán mediante cambios de versión.
