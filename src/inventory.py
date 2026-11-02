import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class Unidad:
    """Modelo de datos para una unidad de inventario."""
    id: str
    equipment: str


class InventoryManager:
    """Gestiona el inventario fijo de equipos."""
    
    def __init__(self, inventory_path: str = "data/inventory.json"):
        self.inventory_path = Path(inventory_path)
        self._unidades: Optional[List[Unidad]] = None
    
    def cargar_inventario(self) -> List[Unidad]:
        """Carga el inventario desde el archivo JSON."""
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Archivo de inventario no encontrado: {self.inventory_path}")
        
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._unidades = [Unidad(item['id'], item['equipment']) for item in data]
        return self._unidades
    
    def obtener_unidades(self) -> List[Unidad]:
        """Obtiene la lista de unidades (carga si no está cargada)."""
        if self._unidades is None:
            return self.cargar_inventario()
        return self._unidades
    
    def validar_unidad_id(self, unidad_id: str) -> bool:
        """Verifica si un ID de unidad existe en el inventario."""
        unidades = self.obtener_unidades()
        return any(u.id == unidad_id for u in unidades)
    
    def obtener_unidad_por_id(self, unidad_id: str) -> Optional[Unidad]:
        """Obtiene una unidad por su ID, o None si no existe."""
        unidades = self.obtener_unidades()
        for unidad in unidades:
            if unidad.id == unidad_id:
                return unidad
        return None
