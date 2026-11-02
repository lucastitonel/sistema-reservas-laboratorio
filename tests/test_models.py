import pytest
from datetime import datetime, timezone
from src.models import Reserva, validar_solicitante, validar_fechas


class TestValidarSolicitante:
    """Pruebas para la validación de solicitantes."""
    
    def test_solicitante_valido(self):
        """Un solicitante válido debe pasar la validación."""
        valido, error = validar_solicitante("Juan Pérez")
        assert valido is True
        assert error is None
    
    def test_solicitante_vacio(self):
        """Un solicitante vacío debe ser rechazado."""
        valido, error = validar_solicitante("")
        assert valido is False
        assert error == "El solicitante no puede estar vacío"
    
    def test_solicitante_solo_espacios(self):
        """Un solicitante con solo espacios debe ser rechazado."""
        valido, error = validar_solicitante("   ")
        assert valido is False
        assert error == "El solicitante no puede contener solo espacios"
    
    def test_solicitante_con_espacios_externos(self):
        """Un solicitante con espacios externos debe ser aceptado después de limpiar."""
        valido, error = validar_solicitante("  Juan Pérez  ")
        assert valido is True
        assert error is None
    
    def test_solicitante_menos_de_200_caracteres(self):
        """Un solicitante con menos de 200 caracteres debe ser aceptado."""
        solicitante = "A" * 199
        valido, error = validar_solicitante(solicitante)
        assert valido is True
        assert error is None
    
    def test_solicitante_exactamente_200_caracteres(self):
        """Un solicitante con exactamente 200 caracteres debe ser aceptado."""
        solicitante = "A" * 200
        valido, error = validar_solicitante(solicitante)
        assert valido is True
        assert error is None
    
    def test_solicitante_mas_de_200_caracteres(self):
        """Un solicitante con más de 200 caracteres debe ser rechazado."""
        solicitante = "A" * 201
        valido, error = validar_solicitante(solicitante)
        assert valido is False
        assert error == "El solicitante no puede exceder 200 caracteres"


class TestValidarFechas:
    """Pruebas para la validación de fechas."""
    
    def test_fechas_validas(self):
        """Un intervalo válido debe pasar la validación."""
        inicio = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        valido, error = validar_fechas(inicio, fin)
        assert valido is True
        assert error is None
    
    def test_inicio_igual_a_fin(self):
        """Inicio igual a fin debe ser rechazado."""
        inicio = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        valido, error = validar_fechas(inicio, fin)
        assert valido is False
        assert error == "La fecha de inicio debe ser estrictamente anterior a la fecha de fin"
    
    def test_inicio_posterior_a_fin(self):
        """Inicio posterior a fin debe ser rechazado."""
        inicio = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        valido, error = validar_fechas(inicio, fin)
        assert valido is False
        assert error == "La fecha de inicio debe ser estrictamente anterior a la fecha de fin"


class TestReserva:
    """Pruebas para el modelo de Reserva."""
    
    def test_crear_nueva_reserva(self):
        """Crear una nueva reserva debe generar un ID y estado activa."""
        inicio = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        
        reserva = Reserva.crear_nueva(
            unidad_id="MIC-01",
            solicitante="Juan Pérez",
            inicio_utc=inicio,
            fin_utc=fin
        )
        
        assert reserva.unidad_id == "MIC-01"
        assert reserva.solicitante == "Juan Pérez"
        assert reserva.estado == "activa"
        assert reserva.id is not None
        assert len(reserva.id) > 0
        assert reserva.inicio == inicio.isoformat()
        assert reserva.fin == fin.isoformat()
        assert reserva.fecha_creacion is not None
    
    def test_reserva_id_unico(self):
        """Cada reserva debe tener un ID único."""
        inicio = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
        fin = datetime(2026, 11, 2, 11, 0, tzinfo=timezone.utc)
        
        reserva1 = Reserva.crear_nueva("MIC-01", "Juan", inicio, fin)
        reserva2 = Reserva.crear_nueva("MIC-01", "Maria", inicio, fin)
        
        assert reserva1.id != reserva2.id
