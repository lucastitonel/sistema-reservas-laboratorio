import pytest
import json
import tempfile
from pathlib import Path
from src.inventory import InventoryManager, Unidad


class TestInventoryManager:
    """Pruebas para el gestor de inventario."""
    
    def test_cargar_inventario_desde_archivo_existente(self):
        """Cargar el inventario desde el archivo existente debe funcionar."""
        manager = InventoryManager("data/inventory.json")
        unidades = manager.cargar_inventario()
        
        assert len(unidades) == 5
        assert all(isinstance(u, Unidad) for u in unidades)
        
        # Verificar IDs conocidos
        ids = [u.id for u in unidades]
        assert "MIC-01" in ids
        assert "MIC-02" in ids
        assert "OSC-01" in ids
        assert "MUL-01" in ids
        assert "FUE-01" in ids
    
    def test_obtener_unidades_carga_automáticamente(self):
        """Obtener unidades debe cargar automáticamente si no están cargadas."""
        manager = InventoryManager("data/inventory.json")
        # Primera llamada - debe cargar
        unidades1 = manager.obtener_unidades()
        # Segunda llamada - debe usar cache
        unidades2 = manager.obtener_unidades()
        
        assert len(unidades1) == 5
        assert len(unidades2) == 5
        assert unidades1 == unidades2
    
    def test_validar_unidad_id_existente(self):
        """Validar un ID existente debe retornar True."""
        manager = InventoryManager("data/inventory.json")
        assert manager.validar_unidad_id("MIC-01") is True
        assert manager.validar_unidad_id("FUE-01") is True
    
    def test_validar_unidad_id_inexistente(self):
        """Validar un ID inexistente debe retornar False."""
        manager = InventoryManager("data/inventory.json")
        assert manager.validar_unidad_id("XYZ-99") is False
        assert manager.validar_unidad_id("") is False
    
    def test_obtener_unidad_por_id_existente(self):
        """Obtener una unidad por ID existente debe retornar la unidad."""
        manager = InventoryManager("data/inventory.json")
        unidad = manager.obtener_unidad_por_id("MIC-01")
        
        assert unidad is not None
        assert unidad.id == "MIC-01"
        assert unidad.equipment == "Microscopio digital"
    
    def test_obtener_unidad_por_id_inexistente(self):
        """Obtener una unidad por ID inexistente debe retornar None."""
        manager = InventoryManager("data/inventory.json")
        unidad = manager.obtener_unidad_por_id("XYZ-99")
        
        assert unidad is None
    
    def test_archivo_inexistente_lanza_excepcion(self):
        """Intentar cargar un archivo inexistente debe lanzar FileNotFoundError."""
        manager = InventoryManager("ruta/inexistente.json")
        
        with pytest.raises(FileNotFoundError):
            manager.cargar_inventario()
    
    def test_inventario_con_archivo_temporal(self):
        """Cargar inventario desde un archivo temporal personalizado."""
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump([
                {"id": "TEST-01", "equipment": "Equipo de prueba"},
                {"id": "TEST-02", "equipment": "Otro equipo"}
            ], f)
        
        try:
            manager = InventoryManager(temp_path)
            unidades = manager.cargar_inventario()
            
            assert len(unidades) == 2
            assert unidades[0].id == "TEST-01"
            assert unidades[0].equipment == "Equipo de prueba"
            assert unidades[1].id == "TEST-02"
            assert unidades[1].equipment == "Otro equipo"
        finally:
            Path(temp_path).unlink()
