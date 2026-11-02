import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from src.database import DatabaseManager
from src.models import Reserva


class TestDatabaseManager:
    """Pruebas para el gestor de base de datos."""
    
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
    def reserva_sample(self):
        """Crea una reserva de ejemplo para las pruebas."""
        inicio = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        return Reserva.crear_nueva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio_utc=inicio,
            fin_utc=fin
        )
    
    def test_inicializar_db_crea_tabla(self, temp_db):
        """Inicializar la base de datos debe crear la tabla de reservas."""
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='reservas'
        """)
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "reservas"
    
    def test_crear_reserva(self, temp_db, reserva_sample):
        """Crear una reserva debe insertarla en la base de datos."""
        temp_db.crear_reserva(reserva_sample)
        
        reserva_recuperada = temp_db.obtener_reserva_por_id(reserva_sample.id)
        
        assert reserva_recuperada is not None
        assert reserva_recuperada['id'] == reserva_sample.id
        assert reserva_recuperada['unidad_id'] == "MIC-01"
        assert reserva_recuperada['solicitante'] == "Juan Pérez"
        assert reserva_recuperada['estado'] == "activa"
    
    def test_obtener_reserva_por_id_inexistente(self, temp_db):
        """Obtener una reserva por ID inexistente debe retornar None."""
        reserva = temp_db.obtener_reserva_por_id("id-inexistente")
        assert reserva is None
    
    def test_cancelar_reserva(self, temp_db, reserva_sample):
        """Cancelar una reserva debe cambiar su estado a 'cancelada'."""
        temp_db.crear_reserva(reserva_sample)
        
        resultado = temp_db.cancelar_reserva(reserva_sample.id)
        
        assert resultado is True
        
        reserva_recuperada = temp_db.obtener_reserva_por_id(reserva_sample.id)
        assert reserva_recuperada['estado'] == "cancelada"
    
    def test_cancelar_reserva_inexistente(self, temp_db):
        """Cancelar una reserva inexistente debe retornar False."""
        resultado = temp_db.cancelar_reserva("id-inexistente")
        assert resultado is False
    
    def test_obtener_todas_reservas(self, temp_db):
        """Obtener todas las reservas debe retornar todas las creadas."""
        inicio1 = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        reserva1 = Reserva.crear_nueva("MIC-01", "Juan", inicio1, fin1)
        
        inicio2 = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
        fin2 = datetime(2026, 11, 2, 13, 0, tzinfo=timezone.utc)
        reserva2 = Reserva.crear_nueva("MIC-02", "Maria", inicio2, fin2)
        
        temp_db.crear_reserva(reserva1)
        temp_db.crear_reserva(reserva2)
        
        reservas = temp_db.obtener_reservas()
        
        assert len(reservas) == 2
        ids = [r['id'] for r in reservas]
        assert reserva1.id in ids
        assert reserva2.id in ids
    
    def test_obtener_reservas_por_unidad(self, temp_db):
        """Filtrar por unidad debe retornar solo las reservas de esa unidad."""
        inicio1 = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        reserva1 = Reserva.crear_nueva("MIC-01", "Juan", inicio1, fin1)
        
        inicio2 = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
        fin2 = datetime(2026, 11, 2, 13, 0, tzinfo=timezone.utc)
        reserva2 = Reserva.crear_nueva("MIC-02", "Maria", inicio2, fin2)
        
        inicio3 = datetime(2026, 11, 2, 14, 0, tzinfo=timezone.utc)
        fin3 = datetime(2026, 11, 2, 15, 0, tzinfo=timezone.utc)
        reserva3 = Reserva.crear_nueva("MIC-01", "Pedro", inicio3, fin3)
        
        temp_db.crear_reserva(reserva1)
        temp_db.crear_reserva(reserva2)
        temp_db.crear_reserva(reserva3)
        
        reservas_mic01 = temp_db.obtener_reservas(unidad_id="MIC-01")
        
        assert len(reservas_mic01) == 2
        ids = [r['id'] for r in reservas_mic01]
        assert reserva1.id in ids
        assert reserva3.id in ids
        assert reserva2.id not in ids
    
    def test_obtener_reservas_por_estado(self, temp_db):
        """Filtrar por estado debe retornar solo las reservas con ese estado."""
        inicio1 = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin1 = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        reserva1 = Reserva.crear_nueva("MIC-01", "Juan", inicio1, fin1)
        
        inicio2 = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
        fin2 = datetime(2026, 11, 2, 13, 0, tzinfo=timezone.utc)
        reserva2 = Reserva.crear_nueva("MIC-02", "Maria", inicio2, fin2)
        
        temp_db.crear_reserva(reserva1)
        temp_db.crear_reserva(reserva2)
        temp_db.cancelar_reserva(reserva1.id)
        
        reservas_activas = temp_db.obtener_reservas(estado="activa")
        reservas_canceladas = temp_db.obtener_reservas(estado="cancelada")
        
        assert len(reservas_activas) == 1
        assert len(reservas_canceladas) == 1
        assert reservas_activas[0]['id'] == reserva2.id
        assert reservas_canceladas[0]['id'] == reserva1.id
    
    def test_persistencia_tras_cerrar_conexion(self, temp_db, reserva_sample):
        """
        Crear una reserva, cerrar la conexión y reabrir debe recuperar la reserva
        con sus datos y estado originales.
        """
        # Crear reserva
        temp_db.crear_reserva(reserva_sample)
        id_reserva = reserva_sample.id
        datos_originales = {
            'unidad_id': reserva_sample.unidad_id,
            'solicitante': reserva_sample.solicitante,
            'inicio': reserva_sample.inicio,
            'fin': reserva_sample.fin,
            'estado': reserva_sample.estado
        }
        
        # Cerrar conexión
        temp_db.close()
        
        # Reabrir conexión (crear nueva instancia)
        db_nueva = DatabaseManager(temp_db.db_path)
        db_nueva.inicializar_db()
        
        # Recuperar reserva
        reserva_recuperada = db_nueva.obtener_reserva_por_id(id_reserva)
        
        # Verificar que se recuperó con datos originales
        assert reserva_recuperada is not None
        assert reserva_recuperada['id'] == id_reserva
        assert reserva_recuperada['unidad_id'] == datos_originales['unidad_id']
        assert reserva_recuperada['solicitante'] == datos_originales['solicitante']
        assert reserva_recuperada['inicio'] == datos_originales['inicio']
        assert reserva_recuperada['fin'] == datos_originales['fin']
        assert reserva_recuperada['estado'] == datos_originales['estado']
        
        db_nueva.close()
    
    def test_datetime_a_utc_iso(self, temp_db):
        """Convertir datetime a UTC debe retornar string ISO 8601 correcto."""
        # Crear datetime en Buenos Aires
        from zoneinfo import ZoneInfo
        dt_ba = datetime(2026, 11, 2, 10, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires"))
        
        iso_utc = temp_db.datetime_a_utc_iso(dt_ba)
        
        # 10:00 en BA (-3) = 13:00 en UTC
        assert iso_utc == "2026-11-02T13:00:00+00:00"
    
    def test_datetime_a_utc_iso_sin_zona_horaria_lanza_error(self, temp_db):
        """Convertir datetime sin zona horaria debe lanzar ValueError."""
        dt_sin_zona = datetime(2026, 11, 2, 10, 0)
        
        with pytest.raises(ValueError, match="debe tener información de zona horaria"):
            temp_db.datetime_a_utc_iso(dt_sin_zona)
    
    def test_iso_utc_a_datetime(self, temp_db):
        """Convertir string ISO UTC a datetime debe funcionar correctamente."""
        iso_string = "2026-11-02T13:00:00+00:00"
        dt = temp_db.iso_utc_a_datetime(iso_string)
        
        assert dt.year == 2026
        assert dt.month == 11
        assert dt.day == 2
        assert dt.hour == 13
        assert dt.minute == 0
        assert dt.tzinfo == timezone.utc
    
    def test_iso_utc_a_datetime_sin_offset(self, temp_db):
        """Convertir string ISO sin offset debe lanzar ValueError."""
        iso_string = "2026-11-02T13:00:00"
        
        with pytest.raises(ValueError, match="debe incluir explícitamente el offset UTC"):
            temp_db.iso_utc_a_datetime(iso_string)
    
    def test_iso_utc_a_datetime_offset_no_utc(self, temp_db):
        """Convertir string ISO con offset no UTC debe lanzar ValueError."""
        # Offset +03:00 (Buenos Aires)
        iso_string_ba = "2026-11-02T10:00:00+03:00"
        
        with pytest.raises(ValueError, match="debe tener offset UTC"):
            temp_db.iso_utc_a_datetime(iso_string_ba)
        
        # Offset -05:00 (New York)
        iso_string_ny = "2026-11-02T08:00:00-05:00"
        
        with pytest.raises(ValueError, match="debe tener offset UTC"):
            temp_db.iso_utc_a_datetime(iso_string_ny)
    
    def test_cancelar_reserva_conserva_datos(self, temp_db, reserva_sample):
        """Cancelar una reserva debe conservar todos los datos originales."""
        temp_db.crear_reserva(reserva_sample)
        
        datos_antes = temp_db.obtener_reserva_por_id(reserva_sample.id)
        
        temp_db.cancelar_reserva(reserva_sample.id)
        
        datos_despues = temp_db.obtener_reserva_por_id(reserva_sample.id)
        
        # Verificar que solo cambió el estado
        assert datos_despues['id'] == datos_antes['id']
        assert datos_despues['unidad_id'] == datos_antes['unidad_id']
        assert datos_despues['solicitante'] == datos_antes['solicitante']
        assert datos_despues['inicio'] == datos_antes['inicio']
        assert datos_despues['fin'] == datos_antes['fin']
        assert datos_despues['fecha_creacion'] == datos_antes['fecha_creacion']
        assert datos_despues['estado'] == "cancelada"
        assert datos_antes['estado'] == "activa"
