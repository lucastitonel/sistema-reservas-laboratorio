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
- **Consecuencia:** test_models.py (12 pruebas), test_inventory.py (8 pruebas), test_database.py (14 pruebas). Todas las pruebas pasan.
- **Fecha:** 2026-11-02 (Episodio 2 y 3)

## D-013 — Separación de responsabilidades implementada
- **Estado:** Confirmado.
- **Decisión:** Mover métodos de conversión datetime_a_utc_iso e iso_utc_a_datetime de database.py a reservations.py. database.py solo acepta strings ISO UTC ya normalizados.
- **Motivo:** Acordado en D-011 durante Episodio 3 para evitar duplicación de conversiones y clarificar responsabilidades.
- **Consecuencia:** reservations.py valida y normaliza fechas a UTC antes de operaciones de negocio. database.py persiste valores ya normalizados. Eliminados métodos de conversión de database.py.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-014 — Función única de superposición
- **Estado:** Confirmado.
- **Decisión:** Implementar existe_superposicion() en reservations.py como función única compartida por consulta de disponibilidad y creación de reservas.
- **Motivo:** RN-09 de SPEC.md exige que consulta y creación usen exactamente la misma regla de superposición.
- **Consecuencia:** Ambas operaciones invocan existe_superposicion() con la regla inicio_nuevo < fin_existente AND fin_nuevo > inicio_existente. Solo considera reservas activas de la misma unidad.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-015 — Lógica de negocio centralizada
- **Estado:** Confirmado.
- **Decisión:** Crear src/reservations.py con ReservationManager como módulo central de lógica de negocio. Interfaz (app.py) invoca a reservations.py, no a database.py directamente.
- **Motivo:** Separación clara entre interfaz, negocio y persistencia según arquitectura de SPEC.md.
- **Consecuencia:** ReservationManager implementa crear_reserva, consultar_disponibilidad, cancelar_reserva y listar_reservas. Todas las validaciones y reglas de negocio están centralizadas.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-016 — Normalización de solicitante
- **Estado:** Confirmado.
- **Decisión:** Normalizar solicitante con strip() antes de validar y almacenar.
- **Motivo:** AGENTS.md RN-02 y SPEC.md establecen esta normalización.
- **Consecuencia:** crear_reserva() aplica strip() al solicitante antes de validar y persistir.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-017 — Rechazo de cancelación repetida
- **Estado:** Confirmado.
- **Decisión:** Rechazar intento de cancelar una reserva ya cancelada sin modificar el registro.
- **Motivo:** SPEC.md y AGENTS.md exigen comportamiento claro y sin modificaciones silenciosas.
- **Consecuencia:** cancelar_reserva() verifica estado antes de cancelar y retorna error si ya está cancelada.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-018 — Pruebas de lógica de negocio
- **Estado:** Confirmado.
- **Decisión:** Crear tests/test_reservations.py con 24 pruebas para lógica de negocio de reservas.
- **Motivo:** Verificar todas las reglas de negocio, validaciones y comportamiento de superposición.
- **Consecuencia:** 54 pruebas totales pasando. Desglose actual: test_models.py (12 pruebas), test_inventory.py (8 pruebas), test_database.py (10 pruebas), test_reservations.py (24 pruebas). Pruebas cubren creación válida, unidad inexistente, solicitante inválido, fechas sin zona horaria, superposición, intervalos consecutivos, unidades diferentes, consistencia consulta-creación, cancelación, liberación de intervalo, normalización UTC.
- **Fecha:** 2026-11-02 (Episodio 4)

## D-019 — Interfaz Streamlit
- **Estado:** Confirmado.
- **Decisión:** Implementar src/app.py como punto de entrada de la aplicación web local con Streamlit.
- **Motivo:** SPEC.md y AGENTS.md establecen interfaz web local sencilla accesible desde navegador.
- **Consecuencia:** app.py implementa cuatro secciones: Panel Principal (inventario y resumen), Nueva Reserva (formulario de creación), Consultar Disponibilidad (consulta de intervalos), Historial y Cancelaciones (listado y cancelación). La interfaz invoca ReservationManager sin duplicar lógica de negocio. Zona horaria de controles Streamlit interpretada en America/Argentina/Buenos_Aires. Aplicación inicia con streamlit run src/app.py en puerto 8501.
- **Fecha:** 2026-11-03 (Episodio 5)

## D-020 — Manejo de fechas en Streamlit
- **Estado:** Confirmado.
- **Decisión:** Implementar función auxiliar a_aware_buenos_aires() para convertir datetimes naive de st.datetime_input() a datetimes aware de Argentina antes de pasar a ReservationManager.
- **Motivo:** Detectado durante revisión que st.datetime_input() no tiene parámetro timezone y siempre devuelve datetimes naive. El código original usaba un parámetro inexistente timezone=ZONA_HORARIA. ReservationManager rechaza datetimes sin zona horaria.
- **Consecuencia:** Eliminado parámetro timezone inexistente de st.datetime_input(). Agregada función a_aware_buenos_aires() que interpreta datetimes naive como hora local de Argentina usando replace(tzinfo=ZONA_HORARIA). Agregadas 4 pruebas en tests/test_app.py. ReservationManager sigue siendo responsable de normalizar a UTC.
- **Fecha:** 2026-11-03 (Episodio 5 - corrección)

## D-021 — Conexiones SQLite y Streamlit
- **Estado:** Confirmado.
- **Decisión:** Modificar DatabaseManager para abrir y cerrar una conexión nueva por cada operación, en lugar de mantener una conexión persistente compartida.
- **Motivo:** Detectado error "SQLite objects created in a thread can only be used in that same thread" durante pruebas manuales. @st.cache_resource cachea ReservationManager, que mantenía una conexión SQLite persistente. Streamlit ejecuta reruns en hilos diferentes, causando el error de check_same_thread.
- **Consecuencia:** Eliminada conexión persistente _connection en DatabaseManager. Cada método (inicializar_db, crear_reserva, cancelar_reserva, obtener_reserva_por_id, obtener_reservas) ahora crea una nueva conexión con _get_connection(), ejecuta la operación y cierra la conexión en bloque finally. Persistencia se mantiene en el archivo SQLite. Actualizada prueba test_inicializar_db_crea_tabla que accedía a método interno eliminado.
- **Fecha:** 2026-11-03 (Episodio 5 - corrección)

## D-022 — Estado de confirmación de cancelaciones
- **Estado:** Confirmado.
- **Decisión:** Implementar st.session_state para conservar el ID de la reserva pendiente de cancelación entre reruns de Streamlit.
- **Motivo:** Detectado durante pruebas manuales que el flujo de cancelación no funcionaba. El código original mostraba el botón de confirmación en el mismo rerun que el botón de cancelación, pero Streamlit redibuja la interfaz desde cero en cada rerun, haciendo que el mensaje desapareciera. El botón de confirmación nunca se ejecutaba.
- **Consecuencia:** Agregada inicialización de st.session_state.cancel_confirm en main(). Al presionar "Cancelar Reserva", se guarda el ID en session_state y se ejecuta st.rerun(). En el siguiente rerun, si session_state.cancel_confirm coincide con el ID de la reserva, se muestran botones "Confirmar Cancelación" y "No Cancelar". El estado se limpia después de confirmar o abortar.
- **Fecha:** 2026-11-03 (Episodio 5 - corrección)
