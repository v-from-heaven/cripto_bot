import asyncio
from ib_async import IB

async def verificar_conexion_ib():
    ib = IB()
    print("🔌 Intentando conectar a Interactive Brokers (TWS / Paper Trading)...")
    try:
        # Intentamos conectar al puerto local de Paper Trading (7497)
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        print("🟢 ¡Conexión establecida con éxito a Interactive Brokers!")
        
        account_values = ib.accountSummary()
        print(f"📊 Resumen de cuenta obtenido: {len(account_values)} parámetros leídos.")
        
        ib.disconnect()
        print("🔌 Desconexión segura realizada.")
    except Exception as e:
        print(f"🔴 Error de conexión con Interactive Brokers: {e}")
        print("💡 Recuerda tener la TWS / IB Gateway abierta con el socket API habilitado en el puerto 7497.")

if __name__ == '__main__':
    asyncio.run(verificar_conexion_ib())
