import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.models import Reserva


class DatabaseManager:
    """Gestiona la persistencia de reservas en SQLite."""
    
    def __init__(self, db_path: str = "data/reservas.db"):
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene o crea la conexión a la base de datos."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def inicializar_db(self) -> None:
        """Crea la tabla de reservas si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id TEXT PRIMARY KEY,
                unidad_id TEXT NOT NULL,
                solicitante TEXT NOT NULL,
                inicio TEXT NOT NULL,
                fin TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL
            )
        """)
        conn.commit()
    
    def crear_reserva(self, reserva: Reserva) -> None:
        """Inserta una nueva reserva en la base de datos."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reservas (id, unidad_id, solicitante, inicio, fin, estado, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            reserva.id,
            reserva.unidad_id,
            reserva.solicitante,
            reserva.inicio,
            reserva.fin,
            reserva.estado,
            reserva.fecha_creacion
        ))
        conn.commit()
    
    def cancelar_reserva(self, reserva_id: str) -> bool:
        """
        Cancela una reserva cambiando su estado a 'cancelada'.
        Retorna True si se canceló exitosamente, False si no se encontró.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reservas SET estado = 'cancelada' WHERE id = ?",
            (reserva_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    
    def obtener_reserva_por_id(self, reserva_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por su ID, o None si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def obtener_reservas(
        self,
        unidad_id: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reservas filtrando opcionalmente por unidad y estado.
        Si no se especifican filtros, retorna todas las reservas.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM reservas WHERE 1=1"
        params = []
        
        if unidad_id:
            query += " AND unidad_id = ?"
            params.append(unidad_id)
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY fecha_creacion DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def datetime_a_utc_iso(self, dt: datetime) -> str:
        """
        Convierte un datetime a UTC y retorna su representación ISO 8601.
        El datetime debe tener información de zona horaria.
        """
        if dt.tzinfo is None:
            raise ValueError("El datetime debe tener información de zona horaria")
        
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.isoformat()
    
    def iso_utc_a_datetime(self, iso_string: str) -> datetime:
        """
        Convierte una string ISO 8601 (en UTC) a un objeto datetime con zona horaria UTC.
        El string debe incluir explícitamente el offset UTC (+00:00).
        Rechaza fechas sin offset o con offsets diferentes de UTC.
        """
        dt = datetime.fromisoformat(iso_string)
        
        if dt.tzinfo is None:
            raise ValueError("La fecha ISO debe incluir explícitamente el offset UTC (+00:00)")
        
        # Verificar que el offset sea exactamente UTC (+00:00)
        offset = dt.utcoffset()
        if offset is None or offset.total_seconds() != 0:
            raise ValueError("La fecha ISO debe tener offset UTC (+00:00), no se aceptan otros offsets")
        
        return dt
