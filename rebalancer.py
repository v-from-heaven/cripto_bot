def calculate_rebalance_orders(balances, prices, target_weights, total_portfolio_value):
    """
    Calcula que comprar o vender basandose en el balance actual y los precios de Bitvavo.
    """
    orders = {}
    THRESHOLD = 0.01  # Filtro de desviacion del 1%

    print("\n[Leopold] Analizando desviaciones del portafolio...")

    for market, target_weight in target_weights.items():
        # Extraemos el nombre de la cripto (ej: 'BTC' desde 'BTC/EUR')
        asset = market.split('/')[0]
        
        current_price = prices[market]
        current_qty = balances.get(asset, 0.0)
        
        # Calculamos cuanto vale en EUR lo que tenemos actualmente
        current_value_eur = current_qty * current_price
        current_weight = current_value_eur / total_portfolio_value if total_portfolio_value > 0 else 0
        
        # Lo que idealmente deberiamos tener segun nuestro 40/30/30
        target_value_eur = total_portfolio_value * target_weight
        diff_eur = target_value_eur - current_value_eur
        weight_deviation = abs(target_weight - current_weight)

        print(f" STATUS: {asset} -> Peso Actual: {current_weight*100:.1f}% | Objetivo: {target_weight*100:.1f}% | Desviacion: {weight_deviation*100:.1f}%")

        # Si se desvia mas de la cuenta (1%), disparamos la orden
        if weight_deviation > THRESHOLD:
            amount_to_trade = abs(diff_eur) / current_price
            action = 'BUY' if diff_eur > 0 else 'SELL'
                
            orders[market] = {
                'action': action,
                'amount': round(amount_to_trade, 6),
                'value_eur': round(abs(diff_eur), 2)
            }
        else:
            print(f"  OK: {asset} en rango optimo. Nada que hacer.")

    return orders


