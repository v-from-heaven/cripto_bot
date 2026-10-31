import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Hola desde el búnker de V. Confirma enlace con Google AI Studio."
    )
    print("--- ¡CONEXIÓN EXITOSA! ---")
    print("Respuesta de Gemini:", response.text)
except Exception as e:
    print("Error al conectar:", e)
