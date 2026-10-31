import asyncio
import json
import sys
from ib_async import IB

IB_HOST = '127.0.0.1'
IB_PORT = 7496  # Producción Live
CLIENT_ID = 10
ACCOUNT_ID = 'U18103844'

MIN_ORDER_EUR = 10.0  # Filtro anti-comisiones estricto

async def conectar_ib():
    ib = IB()
    await ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=10)
    return ib

async def tool_get_account_balance():
    try:
        ib = await conectar_ib()
        account_values = await ib.accountSummaryAsync()
        cash = 0.0
        for v in account_values:
            if v.tag == 'TotalCashValue' and v.currency == 'EUR':
                cash = float(v.value)
                break
                
        positions = ib.positions()
        pos_summary = []
        for p in positions:
            if p.account == ACCOUNT_ID:
                pos_summary.append(f"{p.contract.symbol}: {p.position} uds (Coste medio: {p.avgCost})")
                
        ib.disconnect()
        
        res = f"💰 Efectivo disponible en U18103844: {cash:.2f} EUR\n"
        res += "📊 Posiciones activas:\n" + ("\n".join(pos_summary) if pos_summary else "Sin posiciones abiertas.")
        return res
    except Exception as e:
        return f"❌ Error conectando a TWS Live: {str(e)}"

async def tool_check_viability(target_weight: float, total_portfolio_eur: float):
    if total_portfolio_eur * target_weight < MIN_ORDER_EUR:
        return f"⛔ ORDEN BLOQUEADA: Importe inferior al filtro anti-comisiones ({MIN_ORDER_EUR:.2f} EUR)."
    return f"🟢 ORDEN VIABLE: Supera el umbral mínimo de {MIN_ORDER_EUR:.2f} EUR."

async def main():
    # Bucle de escucha estándar para protocolo MCP / JSON-RPC
    print("🛡️ [BÚNKER MCP] Servidor nativo Interactive Brokers Live iniciado en stdio.", file=sys.stderr)
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        try:
            request = json.loads(line)
            method = request.get("method")
            req_id = request.get("id")
            
            if method == "get_account_balance":
                result = await tool_get_account_balance()
                response = {"jsonrpc": "2.0", "result": result, "id": req_id}
            elif method == "check_viability":
                params = request.get("params", {})
                result = await tool_check_viability(params.get("target_weight", 0), params.get("total_portfolio_eur", 0))
                response = {"jsonrpc": "2.0", "result": result, "id": req_id}
            else:
                response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Método no encontrado"}, "id": req_id}
                
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_resp = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}
            print(json.dumps(error_resp), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
