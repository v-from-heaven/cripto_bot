# --- FILTRO DE SEGURIDAD SMOKE TEST ---
MAX_TRADE_EUR = 10.0  # Límite máximo inicial para prueba en producción
MIN_TRADE_EUR = 1.0   # Mínimo operativo Bitvavo

def aplicar_filtro_seguridad(orden, balance_eur_disponible):
    monto_eur = orden.get('monto_eur', 0.0)

    # 1. Ignorar si está por debajo del mínimo de Bitvavo
    if monto_eur < MIN_TRADE_EUR:
        print(f"⚠️ [DESCHARTADA] Órden de {monto_eur:.2f}€ en {orden.get('activo')} (inferior al mínimo de {MIN_TRADE_EUR}€).")
        return None

    # 2. Acotar al máximo permitido por el Smoke Test
    if monto_eur > MAX_TRADE_EUR:
        orden['monto_eur'] = MAX_TRADE_EUR
        orden['ajustada_por_seguridad'] = True
        print(f"🛡️ [ACO TADA] Órden de {orden.get('activo')} ajustada al tope de {MAX_TRADE_EUR}€ por Smoke Test.")

    # 3. Comprobar disponibilidad de saldo EUR en compras
    if orden['accion'] == 'BUY' and orden['monto_eur'] > balance_eur_disponible:
        raise ValueError(f"❌ [ERROR] Saldo EUR insuficiente: Requerido {orden['monto_eur']}€ | Disponible {balance_eur_disponible}€.")

    return orden

# Caso de prueba
if __name__ == "__main__":
    print("🧪 --- INICIANDO SMOKE TEST DE SEGURIDAD ---")
    balance_mock = 8.50  # 8.50€ disponibles en EUR
    
    casos = [
        {'activo': 'BTC', 'accion': 'BUY', 'monto_eur': 0.50},   # Debe descartarse (<1€)
        {'activo': 'ETH', 'accion': 'BUY', 'monto_eur': 15.00},  # Debe acotarse a 10€
        {'activo': 'BTC', 'accion': 'BUY', 'monto_eur': 5.00},   # Debe pasar limpia
    ]

    for ord_test in casos:
        print(f"\nProcesando orden original: {ord_test}")
        try:
            res = aplicar_filtro_seguridad(ord_test, balance_mock)
            if res:
                print(f"✅ Resultado: {res}")
        except Exception as e:
            print(f"{e}")
