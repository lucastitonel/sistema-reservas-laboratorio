# Sistema de reservas del laboratorio

Proyecto académico para la asignatura **Tópicos Avanzados de Ingeniería del Software**.

## 1. Especificación breve
Consultar [SPEC.md](SPEC.md), que describe el problema, alcance, reglas, supuestos y criterios de aceptación.

## 2. Solución
- **Lenguaje:** Python 3.15.2.
- **Persistencia:** SQLite.
- **Pruebas:** pytest 9.2.0.
- **Interfaz:** Streamlit 1.66.1, aplicación web local y sencilla.
- **Zona horaria de referencia:** `America/Argentina/Buenos_Aires`.
- **Formato de fecha y hora de entrada:** Controles de Streamlit interpretados en zona horaria BA, normalizados a UTC para almacenamiento.

## 3. Estructura del proyecto

```
sistema-reservas-laboratorio/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Interfaz Streamlit
│   ├── reservations.py        # Lógica de negocio
│   ├── database.py            # Persistencia SQLite
│   ├── inventory.py           # Gestión de inventario
│   └── models.py              # Modelos de datos
├── tests/
│   ├── __init__.py
│   ├── test_app.py            # Pruebas de interfaz (4 pruebas)
│   ├── test_reservations.py   # Pruebas de lógica de negocio (24 pruebas)
│   ├── test_database.py       # Pruebas de persistencia (10 pruebas)
│   ├── test_inventory.py      # Pruebas de inventario (8 pruebas)
│   └── test_models.py         # Pruebas de modelos (12 pruebas)
├── data/
│   ├── inventory.json         # Inventario fijo
│   └── reservas.db            # Base de datos SQLite (generada)
├── docs/
│   ├── decisiones.md           # Registro de decisiones técnicas
│   └── episodios-delegacion.md # Episodios de trabajo con el agente
├── SPEC.md                    # Especificación funcional
├── AGENTS.md                  # Instrucciones para el agente
├── README.md                  # Este archivo
└── requirements.txt           # Dependencias
```

## 4. Instalación y ejecución

### Requisitos previos
- Python 3.15.2
- pip 26.2.2

### Instalación en Windows
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar la aplicación
```bash
# Con el entorno virtual activado
streamlit run src/app.py
```

La aplicación se abrirá en el navegador en `http://localhost:8501`.

### Ejecutar pruebas automatizadas
```bash
# Con el entorno virtual activado
pytest tests/ -v
```

### Datos y persistencia
- La base de datos SQLite se crea automáticamente en `data/reservas.db` al ejecutar la aplicación.
- Las reservas persisten entre ejecuciones de la aplicación.
- El archivo `data/reservas.db` está excluido de Git por `.gitignore`.
- No se requiere reinicio manual de datos; la base de datos se mantiene entre sesiones.

## 5. Secciones de la interfaz

La aplicación Streamlit tiene cuatro secciones accesibles mediante pestañas:

### A. Panel Principal
- Muestra los cinco equipos del inventario con su ID y nombre
- Muestra resumen de reservas activas y canceladas
- Proporciona una vista general del estado del sistema

### B. Nueva Reserva
- Permite seleccionar un equipo del inventario
- Solicita el nombre del solicitante (máximo 200 caracteres)
- Permite seleccionar fecha y hora de inicio y finalización mediante controles
- Valida que el solicitante no esté vacío
- Valida que las fechas tengan zona horaria
- Valida que el inicio sea anterior al fin
- Verifica que no haya superposición con reservas activas existentes
- Muestra confirmación con el ID de reserva generado o error comprensible

### C. Consultar Disponibilidad
- Permite seleccionar un equipo
- Permite seleccionar un intervalo de fechas y horas
- Consulta la disponibilidad usando la misma regla de superposición que la creación
- Muestra claramente si el equipo está disponible o no en el intervalo seleccionado

### D. Historial y Cancelaciones
- Muestra todas las reservas con su información (ID, equipo, solicitante, fechas, estado)
- Permite expandir cada reserva para ver detalles
- Permite cancelar reservas activas con confirmación
- Mantiene las reservas canceladas en el historial
- Actualiza la vista después de cancelar (el intervalo queda disponible)

## 6. Reglas de negocio principales

- Solo se aceptan IDs de equipos existentes en el inventario
- El solicitante es obligatorio, no puede estar vacío ni contener solo espacios
- El solicitante se normaliza con `strip()` antes de validar y almacenar
- Las fechas deben tener información de zona horaria
- El inicio debe ser estrictamente anterior al fin
- Solo las reservas activas bloquean intervalos
- Los intervalos consecutivos están permitidos (ej: 10:00-11:00 y 11:00-12:00)
- Las reservas simultáneas en diferentes equipos están permitidas
- La regla de superposición es: `inicio_nuevo < fin_existente AND fin_nuevo > inicio_existente`
- Cancelar una reserva cambia su estado a 'cancelada' pero no elimina el registro
- Cancelar una reserva ya cancelada es rechazado sin modificar el registro
- Las fechas se normalizan a UTC para almacenamiento y comparación
- El inventario es fijo y no se puede modificar desde la aplicación

## 7. Limitaciones conocidas y supuestos

- La aplicación está diseñada para uso local en una sola máquina
- No hay autenticación ni roles de usuario
- No hay servicio de base de datos externo; usa SQLite local
- La interfaz asume que el usuario está en la zona horaria de Argentina
- Los controles de fecha/hora de Streamlit interpretan los valores como hora local de Argentina
- No hay límite de duración para las reservas
- No hay límite de cuántas reservas puede crear un solicitante
- Las reservas pasadas están permitidas
- No hay notificaciones automáticas de vencimiento
- El inventario está hardcoded en `data/inventory.json` y no se puede modificar desde la aplicación

## 4. Preparación del agente
La preparación prevista está documentada en [AGENTS.md](AGENTS.md). Registrar allí el entorno, versión, modelo visible, permisos, instrucciones realmente aplicadas y límites observados. No completar datos que la herramienta no muestre.

## 5. Registro de decisiones y delegación
- [Decisiones técnicas](docs/decisiones.md)
- [Episodios de delegación](docs/episodios-delegacion.md)

Los episodios deben completarse después de cada interacción real con Devin. Vincular cada afirmación con archivos, pruebas, resultados o commits verificables.
