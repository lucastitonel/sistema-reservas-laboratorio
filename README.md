# Sistema de reservas del laboratorio

Proyecto académico para la asignatura **Tópicos Avanzados de Ingeniería del Software**.

## 1. Especificación breve
Consultar [SPEC.md](SPEC.md), que describe el problema, alcance, reglas, supuestos y criterios de aceptación.

## 2. Solución
- **Lenguaje:** Python.
- **Persistencia prevista:** SQLite.
- **Pruebas previstas:** pytest.
- **Interfaz:** Streamlit, aplicación web local y sencilla.
- **Zona horaria de referencia:** `America/Argentina/Buenos_Aires`.
- **Formato de fecha y hora de entrada:** ISO 8601 con zona horaria explícita.

Los comandos definitivos de instalación, inicialización, ejecución, pruebas y reinicio de datos se completarán cuando el agente implemente la solución. La interfaz se ejecutará localmente con Streamlit y se abrirá en el navegador. No ejecutar un reinicio de datos sobre una base con información que se quiera conservar.

## 3. Preparación del agente
La preparación prevista está documentada en [AGENTS.md](AGENTS.md). Registrar allí el entorno, versión, modelo visible, permisos, instrucciones realmente aplicadas y límites observados. No completar datos que la herramienta no muestre.

## 4. Registro de decisiones y delegación
- [Decisiones técnicas](docs/decisiones.md)
- [Episodios de delegación](docs/episodios-delegacion.md)

Los episodios deben completarse después de cada interacción real con Devin. Vincular cada afirmación con archivos, pruebas, resultados o commits verificables.
