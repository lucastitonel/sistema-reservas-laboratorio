import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from src.reservations import ReservationManager
from src.inventory import InventoryManager
from src.database import DatabaseManager


class TestReservationManager:
    """Pruebas para el gestor de lógica de negocio de reservas."""
    
    @pytest.fixture
    def temp_db(self):
        """Crea una base de datos temporal para las pruebas."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_path = f.name
        
        db = DatabaseManager(temp_path)
        db.inicializar_db()
        
        yield db
        
        db.close()
        Path(temp_path).unlink()
    
    @pytest.fixture
    def inventory(self):
        """Crea un gestor de inventario."""
        return InventoryManager("data/inventory.json")
    
    @pytest.fixture
    def reservation_manager(self, temp_db, inventory):
        """Crea un gestor de reservas con DB temporal e inventario real."""
        return ReservationManager(inventory_manager=inventory, database_manager=temp_db)
    
    @pytest.fixture
    def datetime_ba(self):
        """Fixture para datetime en Buenos Aires."""
        return datetime(2026, 11, 2, 10, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
    
    @pytest.fixture
    def datetime_utc(self):
        """Fixture para datetime en UTC."""
        return datetime(2026, 11, 2, 13, 0, tzinfo=timezone.utc)
    
    def test_crear_reserva_valida(self, reservation_manager, datetime_ba):
        """Crear una reserva válida debe ser exitosa."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is True
        assert error is None
        assert reserva_id is not None
    
    def test_crear_reserva_unidad_inexistente(self, reservation_manager, datetime_ba):
        """Crear reserva con unidad inexistente debe fallar."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="XYZ-99",
            solicitante="Juan Pérez",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert error == "La unidad no existe en el inventario"
        assert reserva_id is None
    
    def test_crear_reserva_solicitante_vacio(self, reservation_manager, datetime_ba):
        """Crear reserva con solicitante vacío debe fallar."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert error == "El solicitante no puede estar vacío"
        assert reserva_id is None
    
    def test_crear_reserva_solicitante_solo_espacios(self, reservation_manager, datetime_ba):
        """Crear reserva con solicitante solo espacios debe fallar."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="   ",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert error == "El solicitante no puede contener solo espacios"
        assert reserva_id is None
    
    def test_crear_reserva_fechas_sin_zona_horaria(self, reservation_manager):
        """Crear reserva con fechas sin zona horaria debe fallar."""
        inicio = datetime(2026, 11, 2, 10, 0)
        fin = datetime(2026, 11, 2, 11, 0)
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert error == "Las fechas deben incluir información de zona horaria"
        assert reserva_id is None
    
    def test_crear_reserva_inicio_igual_fin(self, reservation_manager, datetime_ba):
        """Crear reserva con inicio igual a fin debe fallar."""
        inicio = datetime_ba
        fin = datetime_ba
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert "estrictamente anterior" in error
        assert reserva_id is None
    
    def test_crear_reserva_inicio_posterior_fin(self, reservation_manager, datetime_ba):
        """Crear reserva con inicio posterior a fin debe fallar."""
        inicio = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin = datetime_ba
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is False
        assert "estrictamente anterior" in error
        assert reserva_id is None
    
    def test_crear_reserva_superposicion_rechazada(self, reservation_manager, datetime_ba):
        """Crear reserva con superposición debe ser rechazada."""
        # Primera reserva: 10:00-11:00
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        # Segunda reserva superpuesta: 10:30-11:30
        inicio2 = datetime(2026, 11, 2, 10, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin2 = datetime(2026, 11, 2, 11, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito2, error2, id2 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Maria",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito2 is False
        assert "superposición" in error2
        assert id2 is None
    
    def test_crear_reserva_intervalos_consecutivos_permitidos(self, reservation_manager, datetime_ba):
        """Intervalos consecutivos deben ser permitidos."""
        # Primera reserva: 10:00-11:00
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        # Segunda reserva consecutiva: 11:00-12:00
        inicio2 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin2 = datetime(2026, 11, 2, 12, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito2, error2, id2 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Maria",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito2 is True
        assert error2 is None
        assert id2 is not None
    
    def test_crear_reserva_unidades_diferentes_simultaneas(self, reservation_manager, datetime_ba):
        """Reservas simultáneas en unidades diferentes deben ser permitidas."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        # Reserva en MIC-01
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio,
            fin=fin
        )
        
        assert exito1 is True
        
        # Reserva simultánea en MIC-02
        exito2, error2, id2 = reservation_manager.crear_reserva(
            unidad_id="MIC-02",
            solicitante="Maria",
            inicio=inicio,
            fin=fin
        )
        
        assert exito2 is True
        assert error2 is None
        assert id2 is not None
    
    def test_consultar_disponibilidad_disponible(self, reservation_manager, datetime_ba):
        """Consultar disponibilidad en intervalo libre debe indicar disponible."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito, error, disponible = reservation_manager.consultar_disponibilidad(
            unidad_id="MIC-01",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is True
        assert error is None
        assert disponible is True
    
    def test_consultar_disponibilidad_no_disponible(self, reservation_manager, datetime_ba):
        """Consultar disponibilidad en intervalo ocupado debe indicar no disponible."""
        # Crear reserva: 10:00-11:00
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        # Consultar disponibilidad en intervalo superpuesto: 10:30-11:30
        inicio2 = datetime(2026, 11, 2, 10, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin2 = datetime(2026, 11, 2, 11, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito2, error2, disponible = reservation_manager.consultar_disponibilidad(
            unidad_id="MIC-01",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito2 is True
        assert error2 is None
        assert disponible is False
    
    def test_consulta_creacion_consistentes(self, reservation_manager, datetime_ba):
        """Consulta y creación deben usar la misma lógica de superposición."""
        # Crear reserva: 10:00-11:00
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        # Consultar disponibilidad en intervalo superpuesto: 10:30-11:30
        inicio2 = datetime(2026, 11, 2, 10, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin2 = datetime(2026, 11, 2, 11, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito2, error2, disponible = reservation_manager.consultar_disponibilidad(
            unidad_id="MIC-01",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito2 is True
        assert disponible is False
        
        # Intentar crear en el mismo intervalo superpuesto
        exito3, error3, id3 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Maria",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito3 is False
        assert "superposición" in error3
    
    def test_cancelar_reserva(self, reservation_manager, datetime_ba):
        """Cancelar una reserva debe cambiar su estado a cancelada."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio,
            fin=fin
        )
        
        assert exito1 is True
        
        exito2, error2 = reservation_manager.cancelar_reserva(reserva_id)
        
        assert exito2 is True
        assert error2 is None
        
        # Verificar que la reserva está cancelada
        reservas = reservation_manager.listar_reservas()
        reserva_cancelada = [r for r in reservas if r['id'] == reserva_id][0]
        assert reserva_cancelada['estado'] == 'cancelada'
    
    def test_cancelar_reserva_inexistente(self, reservation_manager):
        """Cancelar una reserva inexistente debe fallar."""
        exito, error = reservation_manager.cancelar_reserva("id-inexistente")
        
        assert exito is False
        assert error == "La reserva no existe"
    
    def test_cancelar_reserva_ya_cancelada(self, reservation_manager, datetime_ba):
        """Cancelar una reserva ya cancelada debe fallar."""
        inicio = datetime_ba
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio,
            fin=fin
        )
        
        assert exito1 is True
        
        # Primera cancelación
        exito2, error2 = reservation_manager.cancelar_reserva(reserva_id)
        assert exito2 is True
        
        # Segunda cancelación
        exito3, error3 = reservation_manager.cancelar_reserva(reserva_id)
        
        assert exito3 is False
        assert error3 == "La reserva ya está cancelada"
    
    def test_cancelar_liberar_intervalo(self, reservation_manager, datetime_ba):
        """Cancelar una reserva debe liberar el intervalo para nuevas reservas."""
        # Primera reserva: 10:00-11:00
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        # Intentar crear reserva superpuesta: debe fallar
        inicio2 = datetime(2026, 11, 2, 10, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        fin2 = datetime(2026, 11, 2, 11, 30, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito2, error2, id2 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Maria",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito2 is False
        
        # Cancelar primera reserva
        exito3, error3 = reservation_manager.cancelar_reserva(id1)
        assert exito3 is True
        
        # Intentar crear reserva en el mismo intervalo: debe ser exitoso
        exito4, error4, id4 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Pedro",
            inicio=inicio2,
            fin=fin2
        )
        
        assert exito4 is True
        assert error4 is None
        assert id4 is not None
    
    def test_listar_reservas(self, reservation_manager, datetime_ba):
        """Listar reservas debe retornar todas las reservas."""
        inicio1 = datetime_ba
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        exito1, error1, id1 = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio1,
            fin=fin1
        )
        
        assert exito1 is True
        
        reservas = reservation_manager.listar_reservas()
        
        assert len(reservas) == 1
        assert reservas[0]['id'] == id1
        assert reservas[0]['estado'] == 'activa'
    
    def test_normalizacion_utc(self, reservation_manager, datetime_ba):
        """Las fechas deben normalizarse correctamente a UTC."""
        inicio = datetime_ba  # 10:00 BA = 13:00 UTC
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))  # 11:00 BA = 14:00 UTC
        
        exito, error, reserva_id = reservation_manager.crear_reserva(
            unidad_id="MIC-01",
            solicitante="Juan",
            inicio=inicio,
            fin=fin
        )
        
        assert exito is True
        
        # Obtener reserva desde DB
        reservas = reservation_manager.listar_reservas()
        reserva = reservas[0]
        
        # Verificar que están en UTC
        assert reserva['inicio'] == "2026-11-02T13:00:00+00:00"
        assert reserva['fin'] == "2026-11-02T14:00:00+00:00"
    
    def test_datetime_a_utc_iso(self, reservation_manager):
        """Convertir datetime a UTC debe retornar string ISO 8601 correcto."""
        dt_ba = datetime(2026, 11, 2, 10, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        iso_utc = reservation_manager.datetime_a_utc_iso(dt_ba)
        
        # 10:00 en BA (-3) = 13:00 en UTC
        assert iso_utc == "2026-11-02T13:00:00+00:00"
    
    def test_datetime_a_utc_iso_sin_zona_horaria_lanza_error(self, reservation_manager):
        """Convertir datetime sin zona horaria debe lanzar ValueError."""
        dt_sin_zona = datetime(2026, 11, 2, 10, 0)
        
        with pytest.raises(ValueError, match="debe tener información de zona horaria"):
            reservation_manager.datetime_a_utc_iso(dt_sin_zona)
    
    def test_iso_utc_a_datetime(self, reservation_manager):
        """Convertir string ISO UTC a datetime debe funcionar correctamente."""
        iso_string = "2026-11-02T13:00:00+00:00"
        dt = reservation_manager.iso_utc_a_datetime(iso_string)
        
        assert dt.year == 2026
        assert dt.month == 11
        assert dt.day == 2
        assert dt.hour == 13
        assert dt.minute == 0
        assert dt.tzinfo == timezone.utc
    
    def test_iso_utc_a_datetime_sin_offset(self, reservation_manager):
        """Convertir string ISO sin offset debe lanzar ValueError."""
        iso_string = "2026-11-02T13:00:00"
        
        with pytest.raises(ValueError, match="debe incluir explícitamente el offset UTC"):
            reservation_manager.iso_utc_a_datetime(iso_string)
    
    def test_iso_utc_a_datetime_offset_no_utc(self, reservation_manager):
        """Convertir string ISO con offset no UTC debe lanzar ValueError."""
        # Offset +03:00 (Buenos Aires)
        iso_string_ba = "2026-11-02T10:00:00+03:00"
        
        with pytest.raises(ValueError, match="debe tener offset UTC"):
            reservation_manager.iso_utc_a_datetime(iso_string_ba)
        
        # Offset -05:00 (New York)
        iso_string_ny = "2026-11-02T08:00:00-05:00"
        
        with pytest.raises(ValueError, match="debe tener offset UTC"):
            reservation_manager.iso_utc_a_datetime(iso_string_ny)
