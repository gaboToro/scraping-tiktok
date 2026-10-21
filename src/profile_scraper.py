import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

COOKIE_PATH = "tiktok_cookies.json"

async def get_profile_info(username: str) -> dict:
    #Formateamos el usuario para que siempre tenga el '@'
    clean_username = username if username.startswith("@") else f"@{username}"
    target_url = f"https://www.tiktok.com/{clean_username}"

    #Usamos las cookies
    if not os.path.exists(COOKIE_PATH):
        raise FileNotFoundError(f"Archivo de sesión '{COOKIE_PATH}' no encontrado. Ejecute session_manager.py primero.")

    print(f"Extrayendo datos de {clean_username}...")
    
    async with async_playwright() as p:
        # Modo headless activado para ejecución silenciosa en segundo plano
        browser = await p.chromium.launch(headless=True)
        
        # Carga del estado de sesión y evasión básica de detección bot
        context = await browser.new_context(
            storage_state=COOKIE_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(target_url, wait_until="domcontentloaded")
        
        try:
            # Espera inteligente al selector de métricas clave para asegurar renderizado de datos
            await page.wait_for_selector('strong[data-e2e="followers-count"]', timeout=10000)
            await page.wait_for_timeout(1000) 
        except Exception:
            print("\n[ALERTA] Tiempo de espera agotado. Verifique el estado de sus cookies o posibles bloqueos.")
            # Si corre en modo headless, no tiene sentido esperar 15 segundos para resolución manual
            pass 

        html = await page.content()
        await browser.close()

    # Procesamiento del DOM para extracción de métricas
    soup = BeautifulSoup(html, "html.parser")

    followers_tag = soup.find("strong", {"data-e2e": "followers-count"})
    following_tag = soup.find("strong", {"data-e2e": "following-count"})
    likes_tag = soup.find("strong", {"data-e2e": "likes-count"})
    bio_tag = soup.find("h2", {"data-e2e": "user-bio"})

    return {
        "username": clean_username,
        "followers": followers_tag.text.strip() if followers_tag else "0",
        "following": following_tag.text.strip() if following_tag else "0",
        "total_likes": likes_tag.text.strip() if likes_tag else "0",
        "bio": bio_tag.text.strip() if bio_tag else "Sin descripción",
    }

if __name__ == "__main__":
    test_user = "lilia_yunda" 
    try:
        data = asyncio.run(get_profile_info(test_user))
        import json
        print("\nResultados:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\nError de extracción: {e}")