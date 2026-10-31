import asyncio
import logging
import urllib.request
import json
from ib_async import IB, MarketOrder, Stock

# Configuración de Logging del Búnker
logging.basicConfig(level=logging.INFO, format='%(asctime)s - 🛡️ [BÚNKER LIVE] - %(message)s')

IB_HOST = '127.0.0.1'
IB_PORT = 7496  # Puerto de Producción Live
CLIENT_ID = 10
ACCOUNT_ID = 'U18103844'

# Reglas Cuantitativas del Portafolio
MIN_ORDER_EUR = 10.0      # Filtro estricto anti-comisiones (Cero pérdidas)
TOLERANCE_THRESHOLD = 0.01  # 1% de desviación permitida

# Credenciales Telegram
TELEGRAM_TOKEN = "8818018639:AAEn9cpVTax0urY1AViNELIYrBMMHS7tdgc"
TELEGRAM_CHAT_ID = "8607448118"

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        logging.error(f"Error enviando alerta a Telegram: {e}")
        return False

async def ejecutar_ciclo_rebalanceo():
    ib = IB()
    try:
        logging.info("Conectando con Interactive Brokers (Producción U18103844)...")
        await ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=10)
        logging.info("🟢 Conexión establecida con éxito.")

        # Obtener valores de cuenta y posiciones
        account_values = await ib.accountSummaryAsync()
        cash = 0.0
        for v in account_values:
            if v.tag == 'TotalCashValue' and v.currency == 'EUR':
                cash = float(v.value)
                break

        positions = ib.positions()
        portfolio_summary = f"💰 Efectivo líquido: {cash:.2f} EUR\n📊 Posiciones Reales:\n"
        
        total_pos_value = 0.0
        pos_details = []
        for p in positions:
            if p.account == ACCOUNT_ID:
                market_val = p.position * p.avgCost # Estimación inicial de valor
                total_pos_value += market_val
                pos_details.append((p.contract.symbol, p.position, market_val))
                portfolio_summary += f"   - {p.contract.symbol}: {p.position} uds\n"

        total_portfolio_eur = cash + total_pos_value
        logging.info(f"Valor total estimado de cartera: {total_portfolio_eur:.2f} EUR")

# Evaluación de reglas cuantitativas y filtro anti-comisiones
    # Si el efectivo supera el mínimo o hay desviaciones operables:
    if cash >= MIN_ORDER_UR:
        logging.info(f"🟢 Viabilidad OK: El efectivo disponible ({cash:.2f} EUR) supera el filtro anti-comisiones.")
        # Aquí se estructurarán las órdenes de rebalanceo automático según los pesos objetivo.
    else:
        logging.info(f"🛑 Liquidez insuficiente para operar sin fricción ({cash:.2f} EUR < {MIN_ORDER_UR} EUR). Esperando aportación o flujo de caja.")

        ib.disconnect()
        logging.info("🔒 Desconexión segura completada.")

    except Exception as e:
        error_msg = f"❌ [ERROR CRÍTICO LIVE] Fallo en el ciclo autónomo: {str(e)}"
        logging.error(error_msg)
        enviar_alerta_telegram(error_msg)

async def bucle_principal():
    enviar_alerta_telegram("🛡️ *Búnker V*: Bot autónomo Live iniciado en Interactive Brokers (U18103844). Monitoreo activo.")
    while True:
        logging.info("Iniciando nuevo ciclo de escaneo cuantitativo...")
        await ejecutar_ciclo_rebalanceo()
        logging.info("💤 Durmiendo 30 minutos hasta el próximo ciclo...")
        await asyncio.sleep(1800)  # Cada 30 minutos

if __name__ == "__main__":
    asyncio.run(bucle_principal())
