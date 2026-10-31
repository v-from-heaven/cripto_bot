import pytest

# --- PARÁMETROS DEL SMOKE TEST ---
MAX_TRADE_EUR = 10.0  # Límite máximo de orden por seguridad en pruebas (10 EUR)
MIN_TRADE_EUR = 1.0   # Mínimo de orden operativo en Bitvavo (~1 EUR)

def filtrar_y_validar_orden(orden, balance_eur_disponible):
    """
    Filtro de seguridad previo a enviar la orden al exchange real.
    Garantiza que no ejecutemos más de lo permitido durante el Smoke Test.
    """
    monto_eur = orden['monto_eur']

    # 1. Verificar mínimo permitido
    if monto_eur < MIN_TRADE_EUR:
        return None  # Se ignora por no llegar al mínimo del exchange

    # 2. Comprabar límite máximo de prueba (Cap de seguridad)
    if monto_eur > MAX_TRADE_EUR:
        orden['monto_eur'] = MAX_TRADE_EUR
        orden['ajustada_por_seguridad'] = True

    # 3. Comprobar disponibilidad de saldo EUR en compras
    if orden['accion'] == 'BUY' and orden['monto_eur'] > balance_eur_disponible:
        raise ValueError(
            f"Saldo EUR insuficiente: Requerido {orden['monto_eur']}€ | Disponible {balance_eur_disponible}€"
        )

    return orden


# =====================================================================
# SUITE DE PRUEBAS UNITARIAS CON PYTEST
# =====================================================================

def test_orden_supera_maximo_y_se_acota():
    """Una orden de 45€ debe ser capada automáticamente a 10€."""
    orden_grande = {'asset': 'ETH', 'accion': 'BUY', 'monto_eur': 45.0}
    balance_eur = 100.0

    orden_filtrada = filtrar_y_validar_orden(orden_grande, balance_eur)
    
    assert orden_filtrada is not None
    assert orden_filtrada['monto_eur'] == MAX_TRADE_EUR
    assert orden_filtrada.get('ajustada_por_seguridad') is True


def test_saldo_insuficiente_lanza_excepcion():
    """Si intentamos comprar por más EUR del disponible, debe abortar."""
    orden = {'asset': 'BTC', 'accion': 'BUY', 'monto_eur': 8.0}
    balance_eur = 3.0  # Solo tenemos 3€ en cuenta

    with pytest.raises(ValueError) as exc_info:
        filtrar_y_validar_orden(orden, balance_eur)
    
    assert "Saldo EUR insuficiente" in str(exc_info.value)


def test_orden_inferior_al_minimo_se_descarta():
    """Una orden de 0.50€ debe ser ignorada por estar bajo el mínimo de Bitvavo."""
    orden_micro = {'asset': 'PAXG', 'accion': 'BUY', 'monto_eur': 0.50}
    balance_eur = 50.0

    orden_filtrada = filtrar_y_validar_orden(orden_micro, balance_eur)
    assert orden_filtrada is None
