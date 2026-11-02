from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Reserva:
    """Modelo de datos para una reserva."""
    id: str
    unidad_id: str
    solicitante: str
    inicio: str  # ISO 8601 en UTC
    fin: str  # ISO 8601 en UTC
    estado: str  # 'activa' o 'cancelada'
    fecha_creacion: str  # ISO 8601 en UTC

    @classmethod
    def crear_nueva(
        cls,
        unidad_id: str,
        solicitante: str,
        inicio_utc: datetime,
        fin_utc: datetime
    ) -> "Reserva":
        """Crea una nueva reserva con ID generado y estado activa."""
        now_utc = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            unidad_id=unidad_id,
            solicitante=solicitante,
            inicio=inicio_utc.isoformat(),
            fin=fin_utc.isoformat(),
            estado="activa",
            fecha_creacion=now_utc.isoformat()
        )


def validar_solicitante(solicitante: str) -> tuple[bool, Optional[str]]:
    """
    Valida el solicitante según las reglas:
    - No puede estar vacío
    - No puede contener solo espacios
    - Máximo 200 caracteres
    """
    if not solicitante:
        return False, "El solicitante no puede estar vacío"
    
    solicitante_limpio = solicitante.strip()
    
    if len(solicitante_limpio) == 0:
        return False, "El solicitante no puede contener solo espacios"
    
    if len(solicitante_limpio) > 200:
        return False, "El solicitante no puede exceder 200 caracteres"
    
    return True, None


def validar_fechas(inicio: datetime, fin: datetime) -> tuple[bool, Optional[str]]:
    """
    Valida que las fechas cumplan las reglas:
    - Inicio debe ser estrictamente anterior a fin
    """
    if inicio >= fin:
        return False, "La fecha de inicio debe ser estrictamente anterior a la fecha de fin"
    
    return True, None
