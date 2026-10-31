import asyncio
from ib_async import IB

IB_HOST = '127.0.0.1'
IB_PORT = 7496  # Puerto de Producción (Live Trading)
CLIENT_ID = 10  # Master API Client ID configurado en TWS

async def conectar_live():
    ib = IB()
    print(f"🛡️ [BÚNKER LIVE] Conectando a Interactive Brokers (Producción) en {IB_HOST}:{IB_PORT}...")
    try:
        await ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=10)
        print("🟢 [BÚNKER LIVE] ¡Conectado a la cuenta real U18103844!")
        
        # Lectura de efectivo en EUR
        account_values = await ib.accountSummaryAsync()
        for v in account_values:
            if v.tag == 'TotalCashValue' and v.currency == 'EUR':
                print(f"💰 Efectivo líquido real: {v.value} {v.currency}")
                
        # Lectura de posiciones reales (BUNH, IAUP)
        print("\n📊 [TELEMETRÍA LIVE] Posiciones activas en cartera:")
        positions = ib.positions()
        for p in positions:
            if p.account == 'U18103844':
                print(f"   - Activo: {p.contract.symbol} | Cantidad: {p.position} | Coste Medio: {p.avgCost}")
                
        ib.disconnect()
        print("\n🔒 Desconexión segura de producción completada.")
        
    except Exception as e:
        print(f"❌ [ERROR LIVE] Fallo de conexión en producción: {e}")

if __name__ == "__main__":
    asyncio.run(conectar_live())

