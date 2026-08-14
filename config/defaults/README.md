# config/defaults

**Estado:** reservado para valores por defecto no sensibles compartidos entre entornos
(p. ej. timeouts por defecto de ToolCall, wake word por defecto "Tony").

Por ahora esos defaults viven directamente como valores por defecto en `config/settings.py`
y en los propios modelos de `contracts/`. Esta carpeta se activara cuando la cantidad de
configuracion declarativa (politicas, mapeos de dispositivos, etc.) justifique separarla en
archivos propios (YAML/TOML) en lugar de constantes en codigo.
