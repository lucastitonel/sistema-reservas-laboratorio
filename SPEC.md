# Especificación breve — Sistema de reservas del laboratorio

## 1. Problema
La coordinación de un laboratorio registra pedidos mediante mensajes y una planilla. Esto puede producir reservas superpuestas para una misma unidad y cancelaciones que continúan bloqueando horarios. Se necesita una aplicación local pequeña que permita consultar disponibilidad, reservar y cancelar, conservando el historial.

## 2. Alcance
La aplicación será local y tendrá una interfaz web sencilla desarrollada con Streamlit. Se ejecutará en la computadora del usuario y se accederá desde un navegador web local. Permitirá:
- Leer un inventario precargado e inmutable.
- Consultar disponibilidad de una unidad para un intervalo.
- Crear una reserva de una sola unidad mediante un formulario.
- Cancelar una reserva sin borrar sus datos.
- Consultar el historial de reservas activas y canceladas.
- Mostrar un resumen sencillo del inventario y las reservas.
- Persistir reservas y estados entre ejecuciones.

La interfaz tendrá un alcance acotado: dashboard/resumen, formulario de nueva reserva, consulta de disponibilidad e historial con opción de cancelación. No se requiere autenticación ni diseño visual complejo.

Fuera de alcance: administración del inventario, autenticación, roles reales, notificaciones, pagos, integraciones externas, despliegue, interfaz gráfica compleja, concurrencia distribuida y escalabilidad de producción.

## 3. Inventario inicial
| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

Cada ID representa una unidad física diferente.

## 4. Requisitos funcionales verificables
- RF-01: listar el inventario precargado.
- RF-02: consultar disponibilidad por ID de unidad e intervalo.
- RF-03: crear una reserva con identificador, unidad, solicitante, inicio, fin y estado.
- RF-04: cancelar una reserva existente conservando identificador y datos originales.
- RF-05: recuperar reservas y estados luego de cerrar y reiniciar la aplicación.

## 5. Reglas de negocio y validaciones
- RN-01: solo se aceptan IDs presentes en el inventario.
- RN-02: el solicitante no puede estar vacío ni contener solamente espacios.
- RN-03: las fechas y horas deben ser válidas.
- RN-04: el inicio debe ser estrictamente anterior al fin.
- RN-05: una reserva activa ocupa su intervalo; una cancelada no bloquea disponibilidad.
- RN-06: se rechazan superposiciones entre reservas activas de la misma unidad.
- RN-07: se permiten intervalos consecutivos: [10:00, 11:00) y [11:00, 12:00).
- RN-08: unidades diferentes pueden reservarse en intervalos simultáneos.
- RN-09: la consulta de disponibilidad debe aplicar exactamente la misma regla de superposición que la creación de reservas.
- RN-10: cancelar no elimina físicamente la reserva ni altera sus datos originales; solo cambia su estado.

Para dos intervalos, existe superposición cuando `inicio_nuevo < fin_existente` y `fin_nuevo > inicio_existente`, considerando únicamente reservas activas de la misma unidad.

## 6. Supuestos técnicos iniciales
Estos supuestos completan aspectos no definidos en la consigna y deberán mantenerse coherentes en implementación, pruebas y README:
- Zona horaria de negocio: `America/Argentina/Buenos_Aires`.
- Entrada de fecha y hora: ISO 8601 con desplazamiento horario explícito. Normalizar los instantes para compararlos y persistirlos de forma inequívoca.
- No se rechazan reservas por estar en el pasado: la consigna no establece esa restricción y se prioriza conservar un historial verificable.
- No se fija duración máxima ni anticipación máxima para reservar.
- Los identificadores de reserva serán únicos y generados por la aplicación.
- El inventario se carga desde `data/inventory.json` y no se modifica desde las operaciones de usuario.
- Los datos de reservas se guardan en un archivo SQLite local dentro de `data/`.
- La interfaz Streamlit es una capa de presentación: no debe contener reglas de negocio ni consultas SQL dispersas. Debe invocar funciones de los módulos de lógica de negocio y persistencia.
- La lógica de reservas debe poder probarse automáticamente sin iniciar la interfaz Streamlit.
- El solicitante se normaliza eliminando espacios al principio y al final; luego se valida que no esté vacío y que no supere los 200 caracteres.
- Si se intenta cancelar una reserva ya cancelada, la operación debe rechazarse con un mensaje claro y sin modificar el registro.

Si el agente propone cambiar alguno de estos supuestos, debe explicar el motivo y esperar revisión humana antes de incorporarlo.

## 7. Criterios de aceptación
- CA-01: se puede listar el inventario inicial completo.
- CA-02: se crea una reserva válida y se obtiene un identificador.
- CA-03: una reserva superpuesta para la misma unidad es rechazada.
- CA-04: una reserva consecutiva para la misma unidad es aceptada.
- CA-05: una reserva simultánea para otra unidad es aceptada.
- CA-06: se rechazan unidad desconocida, solicitante vacío/espacios, fechas inválidas e inicio igual o posterior al fin.
- CA-07: cancelar conserva la reserva y libera el intervalo.
- CA-08: disponibilidad y creación coinciden en su criterio de superposición.
- CA-09: reservas activas y canceladas se recuperan tras reiniciar la aplicación.
- CA-10: las pruebas se pueden ejecutar localmente siguiendo instrucciones del README.
- CA-11: la interfaz permite crear reservas, consultar disponibilidad, consultar el historial y cancelar reservas.
- CA-12: las fechas se ingresan mediante controles amigables de la interfaz y se interpretan en la zona `America/Argentina/Buenos_Aires`, convirtiéndose a UTC internamente.
- CA-13: las operaciones principales de la lógica de negocio pueden probarse sin iniciar Streamlit.

## 8. Verificación requerida
Incluir pruebas automáticas para creación válida, superposición, límites consecutivos, unidades distintas, entradas inválidas y cancelación con conservación del registro y liberación del horario. Verificar también persistencia tras detener y reiniciar la aplicación. Registrar comandos, resultados, fallos y pruebas no ejecutadas.


## 9. Alcance de la interfaz
La interfaz Streamlit debe incluir como mínimo:
- **Resumen:** cantidad de unidades del inventario y resumen de reservas activas.
- **Nueva reserva:** selección de unidad, solicitante, fecha y hora de inicio y fin; mostrar errores de validación y confirmación del resultado.
- **Disponibilidad:** selección de unidad e intervalo y resultado disponible/no disponible.
- **Historial:** listado de reservas, estado y datos principales; permitir cancelar únicamente reservas activas.

La interfaz debe ser simple, clara y funcional. No se requiere calendario avanzado, autenticación, roles, notificaciones, gráficos complejos ni personalización visual extensa.

## 10. Arquitectura de la aplicación
Separar responsabilidades:
- `src/app.py`: interfaz Streamlit y navegación entre secciones.
- `src/reservations.py`: reglas de negocio, validaciones y operaciones de reservas.
- `src/database.py`: inicialización y acceso a SQLite.
- `src/inventory.py`: lectura del inventario.
- `src/models.py`: estructuras de datos, si resultan necesarias.
- `src/main.py`: punto de entrada o arranque de la aplicación, si se utiliza.

La interfaz no debe duplicar la regla de superposición. La consulta de disponibilidad y la creación deben invocar la misma lógica centralizada en la capa de negocio.
