"""Persistencia principal de TONY: PostgreSQL (v0.2 S1, v0.3 S8).

Solo se define aqui el esquema minimo necesario para el hito v0.0.1 (audit_events). Los
demas dominios de v0.3 S8 (identidad, conversacion, memoria, proyectos, ejecucion,
seguridad, IA, automatizacion, domotica, sistema) se agregan en migraciones posteriores,
junto con el paso del orden oficial de implementacion que los necesita.
"""
