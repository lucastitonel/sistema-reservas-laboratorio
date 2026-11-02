# Registro de decisiones técnicas

Registrar decisiones reales, con fecha, contexto, alternativas consideradas, decisión, motivo y consecuencias.

## D-001 — Lenguaje y persistencia
- **Estado:** Confirmado.
- **Decisión:** Python 3.15.2 + SQLite.
- **Motivo:** Solución local pequeña, sin servidor de base de datos. Python 3.15.2 es compatible con pytest 9.2.0 y streamlit 1.66.1.
- **Consecuencia:** Instalación y ejecución reproducibles en un entorno Python con entorno virtual .venv.
- **Fecha:** 2026-11-02 (Episodio 1)

## D-002 — Interfaz
- **Estado:** Confirmado (cambiado desde propuesta original).
- **Decisión:** Interfaz web local con Streamlit (no consola).
- **Motivo:** Usuario solicitó cambio durante Episodio 1 para tener una aplicación web local accesible desde el navegador.
- **Consecuencia:** Punto de entrada previsto en src/app.py (implementación pendiente de etapa posterior). Separación clara entre interfaz (app.py) y lógica de negocio (reservations.py).
- **Fecha:** 2026-11-02 (Episodio 1)

## D-003 — Fechas y zona horaria
- **Estado:** Confirmado.
- **Decisión:** Zona horaria de negocio `America/Argentina/Buenos_Aires`; el usuario seleccionará fechas y horarios mediante controles de Streamlit (no escribe ISO 8601 manualmente); la lógica de negocio normalizará a UTC; entradas ISO 8601 de interfaces externas deben incluir offset explícito.
- **Motivo:** Evitar comparaciones ambiguas entre fechas y horas con diferentes offsets. La interfaz amigable con controles elimina la necesidad de que el usuario escriba fechas manualmente.
- **Consecuencia:** La interfaz (app.py) interpretará los controles de Streamlit en zona horaria BA, la lógica de negocio (reservations.py) normalizará a UTC, y la persistencia almacenará strings ISO 8601 con offset +00:00.
- **Fecha:** 2026-11-02 (Episodio 1)

## D-004 — Validación estricta de fechas ISO 8601
- **Estado:** Confirmado.
- **Decisión:** Rechazar fechas ISO sin offset o con offset diferente de UTC (+00:00). No asumir UTC silenciosamente.
- **Motivo:** Detectado en Episodio 3 que iso_utc_a_datetime() asumía UTC silenciosamente cuando faltaba offset, lo que podía llevar a ambigüedades.
- **Consecuencia:** Método iso_utc_a_datetime() en database.py lanza ValueError si no hay offset o si offset no es +00:00. Prueba test_iso_utc_a_datetime_offset_no_utc verifica rechazo de offsets +03:00 y -05:00.
- **Fecha:** 2026-11-02 (Episodio 3)

## D-005 — Modelo de datos
- **Estado:** Confirmado.
- **Decisión:** Usar dataclass de Python para el modelo Reserva.
- **Motivo:** Simplicidad, claridad y sin dependencias externas.
- **Consecuencia:** Modelo con campos id, unidad_id, solicitante, inicio, fin, estado, fecha_creacion. Método crear_nueva() como classmethod para generar UUID automáticamente.
- **Fecha:** 2026-11-02 (Episodio 2)

## D-006 — Validación de solicitantes
- **Estado:** Confirmado.
- **Decisión:** Solicitante obligatorio, no vacío, no solo espacios, máximo 200 caracteres.
- **Motivo:** Restricción adicional solicitada por el usuario durante aprobación de arquitectura.
- **Consecuencia:** Función validar_solicitante() en models.py implementa estas reglas. Pruebas verifican límites de caracteres y espacios.
- **Fecha:** 2026-11-02 (Episodio 1, confirmado en Episodio 2)

## D-007 — Validación de fechas
- **Estado:** Confirmado.
- **Decisión:** Inicio debe ser estrictamente anterior a fin. No hay duración mínima ni máxima.
- **Motivo:** RN-04 de SPEC.md exige inicio < fin. No se agregaron restricciones arbitrarias no justificadas.
- **Consecuencia:** Función validar_fechas() en models.py verifica orden temporal. Pruebas verifican rechazo de inicio >= fin.
- **Fecha:** 2026-11-02 (Episodio 2)

## D-008 — Inventario
- **Estado:** Confirmado.
- **Decisión:** Inventario fijo cargado desde data/inventory.json. No modificable desde la aplicación.
- **Motivo:** RN-01 y SPEC.md establecen que el inventario es precargado e inmutable.
- **Consecuencia:** InventoryManager en src/inventory.py carga JSON una vez y cachea unidades. Método validar_unidad_id() verifica existencia.
- **Fecha:** 2026-11-02 (Episodio 2)

## D-009 — Identificadores de reserva
- **Estado:** Confirmado.
- **Decisión:** UUID versión 4 generado por la aplicación usando uuid.uuid4().
- **Motivo:** Garantiza unicidad sin depender de configuración externa.
- **Consecuencia:** Cada reserva tiene un ID único generado automáticamente en crear_nueva().
- **Fecha:** 2026-11-02 (Episodio 2)

## D-010 — Persistencia de cancelaciones
- **Estado:** Confirmado.
- **Decisión:** Cancelar una reserva actualiza su estado a 'cancelada' pero no elimina el registro físicamente.
- **Motivo:** RN-10 de SPEC.md exige conservar datos originales y solo cambiar estado.
- **Consecuencia:** Método cancelar_reserva() en database.py hace UPDATE estado = 'cancelada'. Prueba test_cancelar_reserva_conserva_datos verifica que todos los datos originales se mantienen.
- **Fecha:** 2026-11-02 (Episodio 2)

## D-011 — Separación de responsabilidades (pendiente de implementación)
- **Estado:** Acordado, pendiente de implementación en segunda etapa.
- **Decisión:** reservations.py será responsable de validar y normalizar fechas a UTC antes de operaciones de negocio. database.py solo almacenará valores ya normalizados.
- **Motivo:** Acordado durante revisión técnica del Episodio 3 para evitar duplicación de conversiones y clarificar responsabilidades.
- **Consecuencia:** Métodos de conversión datetime_a_utc_iso e iso_utc_a_datetime se moverán de database.py a reservations.py en la segunda etapa. models.py no duplicará validación de zona horaria.
- **Fecha:** 2026-11-02 (Episodio 3)

## D-012 — Pruebas automatizadas
- **Estado:** Confirmado.
- **Decisión:** Usar pytest para pruebas unitarias. 35 pruebas implementadas para modelos, inventario y persistencia.
- **Motivo:** Verificación automatizada de funcionalidad. pytest es compatible con Python 3.15.2.
- **Consecuencia:** test_models.py (13 pruebas), test_inventory.py (8 pruebas), test_database.py (14 pruebas). Todas las pruebas pasan.
- **Fecha:** 2026-11-02 (Episodio 2 y 3)
