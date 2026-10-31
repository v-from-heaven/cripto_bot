import asyncio
from ib_async import IB, util

async def test_ib():
    ib = IB()
    print("🔌 Conectando a Interactive Brokers TWS (Puerto 7497)...")
    try:
        # Intentar conexión a TWS Paper Trading
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        print("🟢 ¡CONEXIÓN EXITOSA CON INTERACTIVE BROKERS!")
        
        # Consultar la hora del servidor de IB
        time = ib.reqCurrentTime()
        print(f"🕒 Hora del servidor IB: {time}")
        
        ib.disconnect()
    except Exception as e:
        print(f"❌ Error de conexión con IB (Asegúrate de tener TWS abierta en el puerto 7497): {e}")

if __name__ == "__main__":
    asyncio.run(test_ib())
