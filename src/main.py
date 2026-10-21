import os
import json
import asyncio

# Importamos las funciones y variables de nuestros módulos
from src.session_manager import generate_session, COOKIE_PATH
from src.profile_scraper import get_profile_info
from src.post_scraper import get_recent_posts

async def run_pipeline():
    print("=" * 50)
    print("      🚀 TIKTOK SCRAPER PRO (SIN EXTENSIONES) 🚀")
    print("=" * 50)
    
    username = input("\nIngresa el username de TikTok a consultar (ej. @tiktok): ").strip()
    if not username:
        print("[ERROR] El usuario no puede estar vacío.")
        return

    # LÓGICA DE COOKIES
    if not os.path.exists(COOKIE_PATH):
        print("\n[PREPARACIÓN] No se encontraron cookies guardadas.")
        print("Generando una nueva sesión (se abrirá el navegador)...")
        await generate_session()
    else:
        print(f"\n[PREPARACIÓN] Sesión encontrada ({COOKIE_PATH}). Reutilizando cookies...")

    # EXTRACCIÓN DEL PERFIL
    print(f"\n[1/2] Extrayendo datos generales del perfil {username}...")
    try:
        profile_data = await get_profile_info(username)
    except Exception as e:
        print(f"[ERROR] Falló la extracción del perfil: {e}")
        return

    # EXTRACCIÓN DE LOS VIDEOS
    print("\n[2/2] Extrayendo métricas de las últimas publicaciones...")
    try:
        posts = await get_recent_posts(username, limit=5)
        profile_data["recent_posts"] = posts
    except Exception as e:
        print(f"[ERROR] Falló la extracción de publicaciones: {e}")
        profile_data["recent_posts"] = []

    # EXPORTACIÓN A JSON
    os.makedirs("reports", exist_ok=True) # Crea la carpeta si no existe por algún motivo
    clean_name = username.replace('@', '')
    output_filename = f"reports/report_{clean_name}.json" # Redirige a la carpeta reports
    
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 50)
    print(f"✅ PROCESO FINALIZADO CON ÉXITO")
    print(f"📁 Los datos han sido guardados en: {output_filename}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_pipeline())