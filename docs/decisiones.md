# Registro de decisiones técnicas

Registrar decisiones reales, con fecha, contexto, alternativas consideradas, decisión, motivo y consecuencias.

## D-001 — Lenguaje y persistencia
- Estado: decisión inicial propuesta.
- Decisión: Python + SQLite.
- Motivo: solución local pequeña, sin servidor de base de datos.
- Consecuencia: instalación y ejecución reproducibles en un entorno Python.

## D-002 — Interfaz
- Estado: decisión inicial propuesta.
- Decisión: interfaz de consola.
- Motivo: la consigna no exige interfaz gráfica.
- Consecuencia: concentrar el esfuerzo en reglas de negocio, persistencia y pruebas.

## D-003 — Fechas y zona horaria
- Estado: decisión inicial propuesta.
- Decisión: zona de negocio `America/Argentina/Buenos_Aires`; entradas ISO 8601 con offset explícito.
- Motivo: evitar comparaciones ambiguas entre fechas y horas.
- Consecuencia: documentar y probar normalización y comparación de instantes.

Actualizar los estados cuando las decisiones se revisen y sean aceptadas por la persona responsable.
