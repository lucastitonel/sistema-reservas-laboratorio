# Instrucciones para el agente de programación

## Objetivo
Implementar el sistema de reservas definido en `SPEC.md`, manteniendo una solución local, pequeña, verificable y fácil de ejecutar.

## Antes de modificar
1. Leer `SPEC.md`, este archivo y el contenido actual del repositorio.
2. Resumir el plan y los archivos que se propone crear o modificar.
3. Identificar ambigüedades o contradicciones antes de asumir requisitos nuevos.
4. No reemplazar decisiones documentadas sin explicar la alternativa y solicitar aprobación humana.

## Restricciones
- Usar Python, SQLite y Streamlit.
- Implementar una interfaz web local, sencilla y funcional, accesible desde un navegador.
- Mantener la lógica de negocio independiente de Streamlit para que pueda probarse sin iniciar la interfaz.
- No agregar autenticación, roles, servicios externos, despliegue ni interfaz gráfica compleja.
- No modificar el inventario desde la aplicación.
- No usar datos personales reales; emplear solicitantes ficticios en ejemplos y pruebas.
- No borrar reservas al cancelar.
- No introducir dependencias innecesarias.
- No incluir secretos, tokens, credenciales ni información privada en archivos o registros.

## Reglas críticas
- Aplicar la misma función/regla de superposición en consulta de disponibilidad y creación.
- Solo las reservas activas bloquean intervalos.
- Comparar intervalos con la regla: `inicio_nuevo < fin_existente` y `fin_nuevo > inicio_existente`.
- Permitir límites consecutivos y reservas simultáneas de unidades diferentes.
- Validar IDs, solicitante, fechas y orden temporal.
- Respetar los supuestos de zona horaria y fechas de `SPEC.md`.
- La interfaz debe permitir seleccionar fecha y hora de manera amigable; no exigir que el usuario escriba ISO 8601 ni offsets.
- Interpretar las fechas seleccionadas en `America/Argentina/Buenos_Aires` y normalizarlas a UTC antes de compararlas y persistirlas.
- Si se reciben fechas desde una API o fuente externa en el futuro, exigir un offset explícito.
- Normalizar el solicitante con `strip()` antes de validar y almacenar; exigir entre 1 y 200 caracteres después de normalizar.
- Rechazar una segunda cancelación de una reserva ya cancelada sin modificar el registro.

## Procedimiento de trabajo
- Trabajar en cambios pequeños y explicables.
- Antes de cada episodio, indicar objetivo, requisito relacionado, contexto utilizado y archivos que se esperan modificar.
- Después de cada cambio, informar archivos modificados, decisiones tomadas, comandos ejecutados y resultados exactos.
- Ejecutar pruebas relevantes; no afirmar que una prueba pasó si no se ejecutó.
- No ocultar fallos ni corregirlos silenciosamente: describirlos y proponer una solución.
- No aceptar automáticamente cambios destructivos, borrados de datos o modificaciones amplias.
- Esperar aprobación humana antes de acciones destructivas o cambios de alcance.
- Mantener `docs/decisiones.md` y `docs/episodios-delegacion.md` actualizados con hechos verificables.

## Adaptación específica comprobable
Para cada operación que consulte o modifique reservas, verificar que la regla de intervalos consecutivos se respete. En particular, agregar y ejecutar una prueba donde una reserva de 10:00 a 11:00 permita otra de 11:00 a 12:00 para la misma unidad, y rechace una de 10:30 a 11:30.

No inventar versiones del modelo, configuraciones, permisos, ejecuciones ni resultados. Si un dato no es visible en el entorno, documentarlo como no disponible.


## Instrucciones específicas para la interfaz Streamlit
- Mantener una interfaz simple con cuatro secciones: resumen, nueva reserva, disponibilidad e historial/cancelación.
- Usar componentes nativos de Streamlit siempre que alcancen; evitar dependencias adicionales de interfaz.
- La interfaz debe invocar la capa de negocio; no implementar reglas de superposición ni SQL directamente en `app.py`.
- Mostrar mensajes claros de éxito, disponibilidad y errores de validación.
- No introducir autenticación, roles, calendarios avanzados, gráficos complejos ni funcionalidades fuera del alcance.
- La aplicación debe poder iniciarse localmente mediante un comando documentado en README.md.
- Las pruebas automáticas centrales deben ejecutarse sin necesidad de levantar el servidor Streamlit.
