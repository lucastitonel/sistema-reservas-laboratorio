import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from src.app import a_aware_buenos_aires, ZONA_HORARIA


class TestAppHelpers:
    """Pruebas para funciones auxiliares de app.py."""

    def test_a_aware_buenos_aires_con_naive(self):
        """Convertir datetime naive a aware de Buenos Aires."""
        dt_naive = datetime(2026, 11, 3, 10, 0)
        dt_aware = a_aware_buenos_aires(dt_naive)

        assert dt_aware.tzinfo == ZONA_HORARIA
        assert dt_aware.year == 2026
        assert dt_aware.month == 11
        assert dt_aware.day == 3
        assert dt_aware.hour == 10
        assert dt_aware.minute == 0

    def test_a_aware_buenos_aires_con_aware_buenos_aires(self):
        """Datetime ya aware de Buenos Aires debe retornarse sin cambios."""
        dt_aware = datetime(2026, 11, 3, 10, 0, tzinfo=ZONA_HORARIA)
        dt_resultado = a_aware_buenos_aires(dt_aware)

        assert dt_resultado == dt_aware
        assert dt_resultado.tzinfo == ZONA_HORARIA

    def test_a_aware_buenos_aires_con_aware_otra_zona(self):
        """Datetime ya aware de otra zona debe retornarse sin cambios."""
        utc = ZoneInfo("UTC")
        dt_aware = datetime(2026, 11, 3, 13, 0, tzinfo=utc)
        dt_resultado = a_aware_buenos_aires(dt_aware)

        assert dt_resultado == dt_aware
        assert dt_resultado.tzinfo == utc

    def test_a_aware_buenos_aires_con_none(self):
        """None debe retornar None."""
        assert a_aware_buenos_aires(None) is None
