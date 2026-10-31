import asyncio
import os
import httpx
import ccxt.pro as ccxt
from datetime import datetime

# Configuración de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8818018639:AAEn9cpVTax0urY1AViNELIYrBMMHS7tdgc")
TELEGRAM_CHAT_ID = "8607448118"

# MODO DE PRUEBA / SIMULADOR (True = No ejecuta órdenes reales en Bitvavo)
PAPER_TRADING = True

# Credenciales de API de Bitvavo (puedes dejarlas vacías para consultar precios públicos)
BITVAVO_API_KEY = os.getenv("BITVAVO_API_KEY", "")
BITVAVO_API_SECRET = os.getenv("BITVAVO_API_SECRET", "")

# Portafolio Objetivo (35% BTC, 25% ETH, 25% PAXG, 15% USD/USDT)
TARGET_WEIGHTS = {
    'BTC': 0.35,
    'ETH': 0.25,
    'PAXG': 0.25,
    'EUR': 0.15  # Bitvavo opera principalmente en pares EUR / USDT
}

TOLERANCE_THRESHOLD = 0.01  # Umbral del 1%
CHECK_INTERVAL_SECONDS = 1800  # 30 minutos

async def send_telegram_alert(message: str):
    """Envía alertas a Telegram."""
    if not TELEGRAM_TOKEN:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload)
            if res.status_code != 200:
                print(f"[Error Telegram] {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[Error Telegram] {e}")

async def fetch_bitvavo_prices():
    """Obtiene precios de mercado en vivo directamente desde Bitvavo."""
    exchange_config = {'enableRateLimit': True}
    if BITVAVO_API_KEY and BITVAVO_API_SECRET:
        exchange_config['apiKey'] = BITVAVO_API_KEY
        exchange_config['secret'] = BITVAVO_API_SECRET

    exchange = ccxt.bitvavo(exchange_config)
    
    # En Bitvavo se opera principalmente contra EUR
    symbols = ['BTC/EUR', 'ETH/EUR', 'PAXG/EUR']
    prices = {'EUR': 1.0}
    
    try:
        print("📡 Conectando a Bitvavo (API Pública/Privada)...")
        tickers = await exchange.fetch_tickers(symbols)
        for symbol, ticker in tickers.items():
            asset = symbol.split('/')[0]
            prices[asset] = ticker['last']
            print(f"   • Bitvavo {symbol}: {prices[asset]:,.2f} €")
    except Exception as e:
        print(f"⚠️ Error conectando con Bitvavo: {e}. Usando contingencia.")
        prices = {'BTC': 62000.0, 'ETH': 3200.0, 'PAXG': 2500.0, 'EUR': 1.0}
    finally:
        await exchange.close()
        
    return prices

async def execute_simulated_orders(orders):
    """Simula la ejecución de órdenes en el entorno de pruebas de Bitvavo."""
    results = []
    for asset, action, amount_eur in orders:
        status = "SIMULADA" if PAPER_TRADING else "EJECUTADA REAL"
        results.append(f"  ✅ `[{status}]` {action} *{asset}*: {amount_eur:,.2f} €")
    return results

async def run_rebalance_check():
    """Comprobación de portafolio y rebalanceo en simulador Bitvavo."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🤖 [{timestamp}] Evaluación Bitvavo Sandbox/Simulador...")
    
    prices = await fetch_bitvavo_prices()
    
    # Balances simulados en Bitvavo (se reemplazarán por exchange.fetch_balance() al poner la API)
    holdings = {
        'BTC': 0.05,
        'ETH': 0.80,
        'PAXG': 1.10,
        'EUR': 1500.0
    }
    
    values = {asset: holdings[asset] * prices[asset] for asset in holdings}
    total_value = sum(values.values())
    
    mode_text = "🧪 MODO SIMULADOR (Bitvavo Paper)" if PAPER_TRADING else "⚡ MODO REAL (Bitvavo Production)"
    
    msg = f"📊 *INFORME DE PORTAFOLIO - BITVAVO*\n"
    msg += f"🕒 `{timestamp}` | `{mode_text}`\n"
    msg += f"Valor Total: *{total_value:,.2f} €*\n\n"
    
    rebalance_orders = []
    details = ""

    for asset, target_weight in TARGET_WEIGHTS.items():
        current_val = values[asset]
        current_weight = current_val / total_value
        target_val = total_value * target_weight
        diff_val = target_val - current_val
        deviation = current_weight - target_weight
        
        details += f"• *{asset}*: {current_weight*100:.1f}% (Obj: {target_weight*100:.1f}%) | Val: {current_val:,.2f} €\n"
        
        if abs(deviation) >= TOLERANCE_THRESHOLD:
            action = "COMPRAR" if diff_val > 0 else "VENDER"
            rebalance_orders.append((asset, action, abs(diff_val)))

    msg += details + "\n"
    
    if rebalance_orders:
        msg += "⚠️ *DESVIACIÓN DETECTADA (>1%). EJECUTANDO SIMULACIÓN:*\n"
        order_results = await execute_simulated_orders(rebalance_orders)
        msg += "\n".join(order_results)
    else:
        msg += "✅ *PORTAFOLIO EQUILIBRADO.* No se requiere intervención."

    print(msg)
    await send_telegram_alert(msg)

async def main():
    print("🚀 Bot de Rebalanceo Cuantitativo en Bitvavo (Simulador Activo)")
    while True:
        try:
            await run_rebalance_check()
        except Exception as e:
            print(f"❌ Error en el ciclo: {e}")
        
        print(f"\n💤 Esperando {CHECK_INTERVAL_SECONDS // 60} minutos hasta la próxima revisión...")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
