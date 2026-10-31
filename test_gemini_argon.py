import os
from openai import OpenAI

# Tomamos la API Key de Vercel
api_key = os.getenv("AI_GATEWAY_API_KEY")

# Inicializamos el cliente apuntando a la base URL de Vercel AI Gateway
client = OpenAI(
    api_key=api_key,
    base_url="https://ai-gateway.vercel.sh/v1"
)

try:
    response = client.chat.completions.create(
        model="google/gemini-4-argon",
        messages=[
            {"role": "user", "content": "Hola, confirma respuesta desde el búnker de V."}
        ]
    )
    print("--- ¡CONEXIÓN EXITOSA! ---")
    print("Respuesta de Gemini Argon:", response.choices[0].message.content)

except Exception as e:
    print("Error al conectar:", e)
