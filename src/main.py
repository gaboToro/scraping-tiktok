import os
import json
import asyncio

from src.session_manager import generate_session, COOKIE_PATH
from src.profile_scraper import get_profile_info
from src.post_scraper import get_recent_posts

async def run_pipeline(username: str):
    clean_username = username if username.startswith("@") else f"@{username}"
    
    print("=" * 50)
    print(f" Iniciando extracción para {clean_username}")
    print("=" * 50)

    if not os.path.exists(COOKIE_PATH):
        print("\n[PREPARACIÓN] No se encontraron cookies guardadas. Generando sesión...")
        await generate_session()
    else:
        print(f"\n[PREPARACIÓN] Reutilizando sesión existente...")

    print(f"\n[1/2] Extrayendo datos del perfil...")
    try:
        profile_data = await get_profile_info(clean_username)
    except Exception as e:
        print(f"[ERROR] Falló la extracción del perfil: {e}")
        return None

    print("\n[2/2] Extrayendo métricas de publicaciones...")
    try:
        posts = await get_recent_posts(clean_username, limit=5)
        profile_data["recent_posts"] = posts
    except Exception as e:
        print(f"[ERROR] Falló la extracción de publicaciones: {e}")
        profile_data["recent_posts"] = []

    os.makedirs("reports", exist_ok=True)
    clean_name = clean_username.replace('@', '')
    output_filename = f"reports/report_{clean_name}.json"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4, ensure_ascii=False)

    print(f"✅ PROCESO FINALIZADO. Datos guardados en: {output_filename}")
    return output_filename # Retornamos la ruta para que la GUI la lea

# Mantenemos el bloque por si quieres ejecutarlo desde consola para pruebas
if __name__ == "__main__":
    test_user = input("Ingresa el username de TikTok: ")
    asyncio.run(run_pipeline(test_user))