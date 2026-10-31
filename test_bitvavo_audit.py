import asyncio
import os
import ccxt.pro as ccxt
from dotenv import load_dotenv

load_dotenv()

async def main():
    exchange = ccxt.bitvavo({
        'apiKey': os.getenv("BITVAVO_API_KEY"),
        'secret': os.getenv("BITVAVO_API_SECRET"),
        'enableRateLimit': True
    })
    
    try:
        balance = await exchange.fetch_balance()
        ticker_usdc = await exchange.fetch_ticker('USDC/EUR')
        precio_usdc_eur = ticker_usdc['last']
        
        print("🔍 --- AUDITORÍA DE SALDOS & LIQUIDEZ USDC EN BITVAVO ---")
        eur_directo = balance['free'].get('EUR', 0.0)
        usdc_total = balance['total'].get('USDC', 0.0)
        usdc_en_eur = usdc_total * precio_usdc_eur
        
        liquidez_total_eur = eur_directo + usdc_en_eur
        
        print(f"💶 EUR Directo Disponible: {eur_directo:.2f} €")
        print(f"💵 USDC Total: {usdc_total:.2f} USDC (Tasa: {precio_usdc_eur:.4f} EUR/USDC)")
        print(f"💰 Equivalencia USDC en EUR: {usdc_en_eur:.2f} €")
        print(f"🟢 LIQUIDEZ TOTAL REAL DISPONIBLE PARA REBALANCEO: {liquidez_total_eur:.2f} €")

    except Exception as e:
        print(f"❌ Error al consultar balance/precios: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
