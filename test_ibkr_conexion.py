import asyncio
from ib_async import IB, Stock

# Parámetros para IBKR en modo Normal/Live
# Usa '10.0.2.2' si TWS/Gateway está en ChromeOS, o '127.0.0.1' si corre dentro de Linux
IBKR_HOST = '127.0.0.1'  
IBKR_PORT = 7496        # 7496 para TWS Live | 4001 para IB Gateway Live (7497 es Paper)

async def verificar_conexion_ibkr():
    ib = IB()
    print(f"[*] Intentando conectar con IBKR Live/Normal en {IBKR_HOST}:{IBKR_PORT}...")
    
    try:
        await ib.connectAsync(IBKR_HOST, IBKR_PORT, clientId=1)
        print("[+] ¡Conexión establecida con éxito en el búnker!")
        
        contrato = Stock('PAXG', 'SMART', 'USD')
        calificaciones = await ib.qualifyContractsAsync(contrato)
        
        if calificaciones:
            print(f"[+] Contrato cualificado: {calificaciones[0]}")
        else:
            print("[-] No se pudo cualificar el contrato.")
            
    except Exception as e:
        print(f"[-] Error en la pasarela IBKR: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("[*] Desconexión segura completada.")

if __name__ == '__main__':
    asyncio.run(verificar_conexion_ibkr())
