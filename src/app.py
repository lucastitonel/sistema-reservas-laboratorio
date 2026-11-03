import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from src.reservations import ReservationManager
from src.inventory import InventoryManager
from src.database import DatabaseManager
from pathlib import Path


# Configuración de la página
st.set_page_config(
    page_title="Sistema de Reservas de Laboratorio",
    page_icon="🔬",
    layout="wide"
)

# Zona horaria de negocio
ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")
DB_PATH = "data/reservas.db"


@st.cache_resource
def get_reservation_manager():
    """Obtiene una instancia única de ReservationManager."""
    inventory = InventoryManager("data/inventory.json")
    database = DatabaseManager(DB_PATH)
    return ReservationManager(inventory_manager=inventory, database_manager=database)


def format_datetime_from_iso(iso_string: str) -> str:
    """Convierte una string ISO UTC a un formato legible en zona horaria BA."""
    dt = datetime.fromisoformat(iso_string)
    dt_ba = dt.astimezone(ZONA_HORARIA)
    return dt_ba.strftime("%d/%m/%Y %H:%M")


def a_aware_buenos_aires(dt_naive: datetime) -> datetime:
    """
    Convierte un datetime naive a datetime aware interpretándolo como hora local de Argentina.
    Si el datetime ya tiene zona horaria, lo retorna sin cambios.
    Si es None, retorna None.
    """
    if dt_naive is None:
        return None
    if dt_naive.tzinfo is not None:
        return dt_naive
    return dt_naive.replace(tzinfo=ZONA_HORARIA)


def main():
    st.title("🔬 Sistema de Reservas de Laboratorio")
    st.markdown("---")

    # Inicializar gestor de reservas
    rm = get_reservation_manager()

    # Inicializar estado de confirmación de cancelación
    if 'cancel_confirm' not in st.session_state:
        st.session_state.cancel_confirm = None

    # Navegación por pestañas
    tab1, tab2, tab3, tab4 = st.tabs([
        "Panel Principal",
        "Nueva Reserva",
        "Consultar Disponibilidad",
        "Historial y Cancelaciones"
    ])

    # ============================================================================
    # TAB 1: Panel Principal
    # ============================================================================
    with tab1:
        st.header("Panel Principal")

        # Mostrar inventario
        st.subheader("Equipos Disponibles")
        unidades = rm.inventory.obtener_unidades()

        if unidades:
            cols = st.columns(len(unidades))
            for i, unidad in enumerate(unidades):
                with cols[i]:
                    st.metric(
                        label=unidad.id,
                        value=unidad.equipment,
                        delta=f"Tipo: {unidad.id.split('-')[0]}"
                    )
        else:
            st.warning("No hay equipos disponibles en el inventario.")

        st.markdown("---")

        # Resumen de reservas
        st.subheader("Resumen de Reservas")
        reservas_activas = rm.listar_reservas(estado="activa")
        reservas_canceladas = rm.listar_reservas(estado="cancelada")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Reservas Activas", len(reservas_activas))
        with col2:
            st.metric("Reservas Canceladas", len(reservas_canceladas))

    # ============================================================================
    # TAB 2: Nueva Reserva
    # ============================================================================
    with tab2:
        st.header("Nueva Reserva")

        # Seleccionar unidad
        unidades = rm.inventory.obtener_unidades()
        opciones_unidades = {u.id: f"{u.id} - {u.equipment}" for u in unidades}
        unidad_id = st.selectbox(
            "Seleccionar Equipo",
            options=list(opciones_unidades.keys()),
            format_func=lambda x: opciones_unidades[x]
        )

        # Ingresar solicitante
        solicitante = st.text_input("Nombre del Solicitante", max_chars=200)

        # Seleccionar fechas y horas
        col1, col2 = st.columns(2)
        with col1:
            inicio_naive = st.datetime_input(
                "Fecha y Hora de Inicio",
                value=datetime.now(ZONA_HORARIA),
                key="inicio"
            )
            inicio = a_aware_buenos_aires(inicio_naive)
        with col2:
            fin_naive = st.datetime_input(
                "Fecha y Hora de Finalización",
                value=datetime.now(ZONA_HORARIA),
                key="fin"
            )
            fin = a_aware_buenos_aires(fin_naive)

        # Botón de confirmación
        if st.button("Crear Reserva", type="primary"):
            # Validar que el solicitante no esté vacío
            if not solicitante or not solicitante.strip():
                st.error("El nombre del solicitante es obligatorio.")
            else:
                # Crear reserva
                exito, error, reserva_id = rm.crear_reserva(
                    unidad_id=unidad_id,
                    solicitante=solicitante,
                    inicio=inicio,
                    fin=fin
                )

                if exito:
                    st.success(f"✅ Reserva creada exitosamente.")
                    st.info(f"ID de reserva: `{reserva_id}`")
                else:
                    st.error(f"❌ Error: {error}")

    # ============================================================================
    # TAB 3: Consultar Disponibilidad
    # ============================================================================
    with tab3:
        st.header("Consultar Disponibilidad")

        # Seleccionar unidad
        unidades = rm.inventory.obtener_unidades()
        opciones_unidades = {u.id: f"{u.id} - {u.equipment}" for u in unidades}
        unidad_id = st.selectbox(
            "Seleccionar Equipo",
            options=list(opciones_unidades.keys()),
            format_func=lambda x: opciones_unidades[x],
            key="disp_unidad"
        )

        # Seleccionar intervalo
        col1, col2 = st.columns(2)
        with col1:
            inicio_naive = st.datetime_input(
                "Fecha y Hora de Inicio",
                value=datetime.now(ZONA_HORARIA),
                key="disp_inicio"
            )
            inicio = a_aware_buenos_aires(inicio_naive)
        with col2:
            fin_naive = st.datetime_input(
                "Fecha y Hora de Finalización",
                value=datetime.now(ZONA_HORARIA),
                key="disp_fin"
            )
            fin = a_aware_buenos_aires(fin_naive)

        # Botón de consulta
        if st.button("Consultar Disponibilidad", type="primary"):
            exito, error, disponible = rm.consultar_disponibilidad(
                unidad_id=unidad_id,
                inicio=inicio,
                fin=fin
            )

            if exito:
                if disponible:
                    st.success(f"✅ El equipo {unidad_id} está disponible en el intervalo seleccionado.")
                else:
                    st.warning(f"⚠️ El equipo {unidad_id} NO está disponible en el intervalo seleccionado.")
            else:
                st.error(f"❌ Error: {error}")

    # ============================================================================
    # TAB 4: Historial y Cancelaciones
    # ============================================================================
    with tab4:
        st.header("Historial de Reservas")

        # Obtener todas las reservas
        reservas = rm.listar_reservas()

        if reservas:
            # Mostrar tabla de reservas
            st.subheader("Todas las Reservas")

            for reserva in reservas:
                with st.expander(
                    f"{reserva['unidad_id']} - {reserva['solicitante']} ({reserva['estado']})"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**ID:** `{reserva['id']}`")
                    with col2:
                        st.write(f"**Inicio:** {format_datetime_from_iso(reserva['inicio'])}")
                    with col3:
                        st.write(f"**Fin:** {format_datetime_from_iso(reserva['fin'])}")

                    st.write(f"**Estado:** {reserva['estado'].upper()}")

                    # Botón de cancelación solo para reservas activas
                    if reserva['estado'] == 'activa':
                        # Verificar si esta reserva está en estado de confirmación
                        if st.session_state.cancel_confirm == reserva['id']:
                            st.warning("⚠️ ¿Estás seguro de cancelar esta reserva?")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button(
                                    f"Confirmar Cancelación de {reserva['id']}",
                                    key=f"confirm_{reserva['id']}"
                                ):
                                    exito, error = rm.cancelar_reserva(reserva['id'])
                                    if exito:
                                        st.success(f"✅ Reserva {reserva['id']} cancelada exitosamente.")
                                        st.session_state.cancel_confirm = None
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Error: {error}")
                            with col_b:
                                if st.button(
                                    f"No Cancelar",
                                    key=f"abort_{reserva['id']}"
                                ):
                                    st.session_state.cancel_confirm = None
                                    st.rerun()
                        else:
                            if st.button(
                                f"Cancelar Reserva {reserva['id']}",
                                key=f"cancel_{reserva['id']}"
                            ):
                                st.session_state.cancel_confirm = reserva['id']
                                st.rerun()
                    else:
                        st.info("Esta reserva ya está cancelada.")

                st.markdown("---")
        else:
            st.info("No hay reservas registradas.")


if __name__ == "__main__":
    main()
