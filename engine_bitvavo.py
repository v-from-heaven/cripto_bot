import asyncio
import urllib.request
import urllib.parse
from config import BITVAVO_API_KEY, BITVAVO_SECRET, TELEGRAM, TELEGRAM_CHAT_ID, TARGET_PORTFOLIO
from rebalancer import calculate_rebalance_orders

def send_telegram_alert(message):
    try:
        import json
        url = "https://telegram.org"
        payload = json.dumps({'chat_id': '8607448118', 'text': message}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='POST')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
    except Exception as e:
        print("ERROR TELEGRAM:", e)

async def main():
    print("[Leopold] Conectando a la infraestructura del sistema...")
    send_telegram_alert("[Leopold] Bot de rebalanceo arrancado en modo simulacion local")

    print("[Leopold - Mock] Detectadas claves vacias (KYC Pending). Activando simulacion local...")
    
    balance_mock = {
        'EUR': 10000.0,
        'BTC': 0.0,
        'ETH': 0.0,
        'PAXG': 0.0
    }
    
    tickers_mock = {
        'BTC/EUR': 62000.0,
        'ETH/EUR': 2400.0,
        'PAXG/EUR': 2350.0
    }
    
    eur_free = balance_mock['EUR']
    markets = list(TARGET_PORTFOLIO.keys())
    
    balances_mapped = {'EUR': eur_free}
    total_portfolio_value = eur_free
    prices = {}
    
    for market in markets:
        asset = market.split('/')[0]
        qty = balance_mock.get(asset, 0.0)
        balances_mapped[asset] = qty
        
        current_price = tickers_mock[market]
        prices[market] = current_price
        total_portfolio_value += (qty * current_price)
        
    print(f"VALOR TOTAL: {total_portfolio_value:.2f} EUR (Efectivo: {eur_free:.2f} EUR)")
    
    orders = calculate_rebalance_orders(balances_mapped, prices, TARGET_PORTFOLIO, total_portfolio_value)
    
    if not orders:
        print("STATUS: Portafolio perfectamente balanceado.")
        send_telegram_alert("STATUS: Balance optimo. El bot no ha necesitado ejecutar ordenes.")
    else:
        for market, details in orders.items():
            alert_text = f"[REBALANCEO LOCAL] {details['action']} {details['amount']} de {market} (Valor: {details['value_eur']} EUR)"
            print(alert_text)
            send_telegram_alert(alert_text)

    print("[Leopold] Ejecucion finalizada. Estructura en orden.")

if __name__ == '__main__':
    asyncio.run(main())
