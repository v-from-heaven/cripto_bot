import pytest
import asyncio

# Configuración del portafolio del búnker
PESOS_OBJETIVO = {
    'BTC': 0.35,
    'ETH': 0.25,
    'PAXG': 0.25,
    'EUR': 0.15
}
UMBRAL_TOLERANCIA = 0.01

def calcular_rebalanceo(balance_actual_eur, precios_eur):
    """
    Calcula el valor objetivo y determina si la desviación supera el 1%.
    """
    valor_total = sum(balance_actual_eur.values())
    desviaciones = {}
    ordenes_simuladas = {}

    for activo, peso_target in PESOS_OBJETIVO.items():
        valor_actual = balance_actual_eur.get(activo, 0.0)
        peso_actual = valor_actual / valor_total
        desviacion = peso_actual - peso_target
        desviaciones[activo] = desviacion

        if abs(desviacion) > UMBRAL_TOLERANCIA:
            diferencia_eur = (peso_target * valor_total) - valor_actual
            ordenes_simuladas[activo] = diferencia_eur

    return valor_total, desviaciones, ordenes_simuladas


def test_no_opera_dentro_del_umbral():
    # Balance perfectamente alineado
    balance_mock = {'BTC': 350.0, 'ETH': 250.0, 'PAXG': 250.0, 'EUR': 150.0}
    precios_mock = {'BTC': 60000, 'ETH': 3000, 'PAXG': 2400, 'EUR': 1}
    
    _, _, ordenes = calcular_rebalanceo(balance_mock, precios_mock)
    assert len(ordenes) == 0, "No debería generar órdenes dentro del umbral"

def test_dispara_ordenes_fuera_del_umbral():
    # BTC subió mucho (desbalanceado)
    balance_mock = {'BTC': 500.0, 'ETH': 200.0, 'PAXG': 200.0, 'EUR': 100.0}
    precios_mock = {'BTC': 60000, 'ETH': 3000, 'PAXG': 2400, 'EUR': 1}
    
    _, _, ordenes = calcular_rebalanceo(balance_mock, precios_mock)
    assert 'BTC' in ordenes, "BTC debería requerir venta por sobrepasar tolerancia"
    assert ordenes['BTC'] < 0, "BTC debe dar una orden de VENTA (monto negativo)"

def test_suma_pesos_es_100_por_ciento():
    assert sum(PESOS_OBJETIVO.values()) == 1.0, "Los pesos objetivo deben sumar exactamente 100%"
