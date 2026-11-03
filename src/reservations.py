from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from src.models import Reserva, validar_solicitante, validar_fechas
from src.inventory import InventoryManager
from src.database import DatabaseManager


class ReservationManager:
    """Gestiona la lógica de negocio de las reservas."""
    
    def __init__(
        self,
        inventory_manager: Optional[InventoryManager] = None,
        database_manager: Optional[DatabaseManager] = None
    ):
        self.inventory = inventory_manager or InventoryManager()
        self.database = database_manager or DatabaseManager()
        self.database.inicializar_db()
    
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
    
    def existe_superposicion(
        self,
        inicio_nuevo: datetime,
        fin_nuevo: datetime,
        reservas_existentes: List[Dict[str, Any]]
    ) -> bool:
        """
        Verifica si existe superposición usando la regla:
        inicio_nuevo < fin_existente AND fin_nuevo > inicio_existente
        Considera únicamente reservas activas de la misma unidad.
        """
        for r in reservas_existentes:
            if r['estado'] != 'activa':
                continue
            
            inicio_existente = self.iso_utc_a_datetime(r['inicio'])
            fin_existente = self.iso_utc_a_datetime(r['fin'])
            
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                return True
        
        return False
    
    def crear_reserva(
        self,
        unidad_id: str,
        solicitante: str,
        inicio: datetime,
        fin: datetime
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Crea una nueva reserva.
        Retorna (exitoso, mensaje_error, reserva_id).
        """
        # Validar unidad
        if not self.inventory.validar_unidad_id(unidad_id):
            return False, "La unidad no existe en el inventario", None
        
        # Validar solicitante
        valido, error = validar_solicitante(solicitante)
        if not valido:
            return False, error, None
        
        # Validar que las fechas tengan zona horaria
        if inicio.tzinfo is None or fin.tzinfo is None:
            return False, "Las fechas deben incluir información de zona horaria", None
        
        # Validar orden temporal
        valido, error = validar_fechas(inicio, fin)
        if not valido:
            return False, error, None
        
        # Normalizar a UTC
        inicio_utc = inicio.astimezone(timezone.utc)
        fin_utc = fin.astimezone(timezone.utc)
        
        # Obtener reservas activas de la unidad
        reservas_activas = self.database.obtener_reservas(
            unidad_id=unidad_id,
            estado='activa'
        )
        
        # Verificar superposición
        if self.existe_superposicion(inicio_utc, fin_utc, reservas_activas):
            return False, "Existe una superposición con una reserva activa existente", None
        
        # Normalizar solicitante
        solicitante_limpio = solicitante.strip()
        
        # Crear reserva
        reserva = Reserva.crear_nueva(
            unidad_id=unidad_id,
            solicitante=solicitante_limpio,
            inicio_utc=inicio_utc,
            fin_utc=fin_utc
        )
        
        # Persistir
        self.database.crear_reserva(reserva)
        
        return True, None, reserva.id
    
    def consultar_disponibilidad(
        self,
        unidad_id: str,
        inicio: datetime,
        fin: datetime
    ) -> Tuple[bool, Optional[str], bool]:
        """
        Consulta disponibilidad de una unidad para un intervalo.
        Retorna (exitoso, mensaje_error, disponible).
        """
        # Validar unidad
        if not self.inventory.validar_unidad_id(unidad_id):
            return False, "La unidad no existe en el inventario", False
        
        # Validar que las fechas tengan zona horaria
        if inicio.tzinfo is None or fin.tzinfo is None:
            return False, "Las fechas deben incluir información de zona horaria", False
        
        # Validar orden temporal
        valido, error = validar_fechas(inicio, fin)
        if not valido:
            return False, error, False
        
        # Normalizar a UTC
        inicio_utc = inicio.astimezone(timezone.utc)
        fin_utc = fin.astimezone(timezone.utc)
        
        # Obtener reservas activas de la unidad
        reservas_activas = self.database.obtener_reservas(
            unidad_id=unidad_id,
            estado='activa'
        )
        
        # Verificar superposición usando la misma función que la creación
        hay_superposicion = self.existe_superposicion(
            inicio_utc,
            fin_utc,
            reservas_activas
        )
        
        disponible = not hay_superposicion
        
        return True, None, disponible
    
    def cancelar_reserva(self, reserva_id: str) -> Tuple[bool, Optional[str]]:
        """
        Cancela una reserva existente.
        Retorna (exitoso, mensaje_error).
        """
        # Verificar que la reserva existe
        reserva = self.database.obtener_reserva_por_id(reserva_id)
        if reserva is None:
            return False, "La reserva no existe"
        
        # Verificar que no esté ya cancelada
        if reserva['estado'] == 'cancelada':
            return False, "La reserva ya está cancelada"
        
        # Cancelar
        exito = self.database.cancelar_reserva(reserva_id)
        
        if exito:
            return True, None
        else:
            return False, "No se pudo cancelar la reserva"
    
    def listar_reservas(
        self,
        unidad_id: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista las reservas, opcionalmente filtradas por unidad y estado.
        """
        return self.database.obtener_reservas(unidad_id=unidad_id, estado=estado)
