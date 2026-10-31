import asyncio
import aiohttp
import urllib3

# Desactivar advertencias de SSL para certificados autofirmados del gateway local de IBKR
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IBKRRESTConector:
    def __init__(self, base_url="https://localhost:5000/v1/api"):
        self.base_url = base_url
        self.session = None

    async def iniciar(self):
        """Inicializa la sesión HTTP asíncrona ignorando la validación SSL local."""
        conn = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=conn)

    async def cerrar(self):
        """Cierra la sesión HTTP limpiamente."""
        if self.session:
            await self.session.close()

    async def verificar_autenticacion(self):
        """Verifica el estado de autenticación de la sesión con el Client Portal Gateway."""
        url = f"{self.base_url}/iserver/auth/status"
        try:
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"🟢 [IBKR REST] Estado de sesión: {data}")
                    return data.get("authenticated", False)
                else:
                    print(f"🔴 [IBKR REST] Error al autenticar. HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️ [IBKR REST] Error de conexión con Gateway: {e}")
            return False

    async def obtener_cuentas(self):
        """Obtiene la lista de cuentas vinculadas (Paper/Live)."""
        url = f"{self.base_url}/portfolio/accounts"
        async with self.session.get(url) as response:
            if response.status == 200:
                cuentas = await response.json()
                print(f"📊 [IBKR REST] Cuentas detectadas: {cuentas}")
                return cuentas
            return []

    async def enviar_micro_orden_prueba(self, account_id, conid, accion="BUY", cantidad=1):
        """
        Envía una micro-orden de prueba en Paper Trading.
        """
        url = f"{self.base_url}/iserver/account/{account_id}/orders"
        
        payload = {
            "orders": [
                {
                    "conid": conid,
                    "orderType": "MKT",
                    "side": accion,
                    "quantity": cantidad,
                    "tif": "DAY"
                }
            ]
        }
        
        print(f"🚀 Enviando MICRO-ORDEN de prueba ({accion} {cantidad} ud, conid: {conid})...")
        async with self.session.post(url, json=payload) as response:
            res_data = await response.json()
            print(f"📩 Respuesta de IBKR Orden: {res_data}")
            return res_data


async def main():
    conector = IBKRRESTConector()
    await conector.iniciar()
    
    print("\n🔍 --- TEST DE CONEXIÓN REST IBKR CLIENT PORTAL ---")
    autenticado = await conector.verificar_autenticacion()
    
    if autenticado:
        cuentas = await conector.obtener_cuentas()
        if cuentas:
            account_id = cuentas[0]['accountId']
            print(f"\n✅ Conexión exitosa con la cuenta: {account_id}")
    else:
        print("\n🔒 El Client Portal Gateway no tiene la sesión autenticada.")
        print("📌 Asegúrate de abrir https://localhost:5000 en el navegador y hacer login en Paper Trading.")

    await conector.cerrar()

if __name__ == "__main__":
    asyncio.run(main())
