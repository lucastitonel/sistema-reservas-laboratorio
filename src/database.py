import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from src.models import Reserva


class DatabaseManager:
    """Gestiona la persistencia de reservas en SQLite."""

    def __init__(self, db_path: str = "data/reservas.db"):
        self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """Crea una nueva conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def close(self) -> None:
        """Método obsoleto: las conexiones se cierran automáticamente después de cada operación."""
        pass
    
    def inicializar_db(self) -> None:
        """Crea la tabla de reservas si no existe."""
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()
    
    def crear_reserva(self, reserva: Reserva) -> None:
        """Inserta una nueva reserva en la base de datos."""
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()
    
    def cancelar_reserva(self, reserva_id: str) -> bool:
        """
        Cancela una reserva cambiando su estado a 'cancelada'.
        Retorna True si se canceló exitosamente, False si no se encontró.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reservas SET estado = 'cancelada' WHERE id = ?",
                (reserva_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def obtener_reserva_por_id(self, reserva_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por su ID, o None si no existe."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def obtener_reservas(
        self,
        unidad_id: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene reservas filtrando opcionalmente por unidad y estado.
        Si no se especifican filtros, retorna todas las reservas.
        """
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()
