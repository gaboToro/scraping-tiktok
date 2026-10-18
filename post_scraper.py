import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

COOKIE_PATH = "tiktok_cookies.json"

async def get_recent_posts(username: str, limit: int = 5) -> list:
    """
    Extrae las métricas (likes, comentarios, compartidos) de las últimas publicaciones
    de un perfil de TikTok, navegando a cada enlace individualmente de forma orgánica.
    """
    clean_username = username if username.startswith("@") else f"@{username}"
    target_url = f"https://www.tiktok.com/{clean_username}"

    if not os.path.exists(COOKIE_PATH):
        raise FileNotFoundError(f"Archivo de sesión '{COOKIE_PATH}' no encontrado. Ejecute session_manager.py primero.")

    print(f"Extrayendo métricas de los últimos {limit} videos de {clean_username}...")
    posts_data = []

    async with async_playwright() as p:
        # Ejecución silenciosa en segundo plano
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=COOKIE_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # --- PARTE 1: CARGAR EL PERFIL ---
        await page.goto(target_url, wait_until="domcontentloaded")
        
        try:
            # Espera a que cargue la cuadrícula de videos
            await page.wait_for_selector('div[data-e2e="user-post-item"]', timeout=15000)
            await page.wait_for_timeout(2000) 
        except Exception:
            print(f"[ALERTA] No se encontró la cuadrícula de videos para {clean_username}.")
            await browser.close()
            return posts_data

        # Validar la cantidad real de videos disponibles
        video_count = await page.locator('div[data-e2e="user-post-item"]').count()
        actual_limit = min(limit, video_count)

        if actual_limit == 0:
            print("No se encontraron videos públicos.")
            await browser.close()
            return posts_data

        # --- PARTE 2: EXTRACCIÓN INDIVIDUAL POR VIDEO ---
        for i in range(actual_limit):
            try:
                # Navegación orgánica mediante clic en la miniatura
                await page.locator('div[data-e2e="user-post-item"] a').nth(i).click()

                # Esperar a que el DOM del video cargue las métricas
                await page.wait_for_selector('strong.video-count', timeout=10000)
                await page.wait_for_timeout(1000)
                
                current_url = page.url
                post_html = await page.content()
                post_soup = BeautifulSoup(post_html, "html.parser")

                metrics = post_soup.find_all("strong", class_="video-count")
                
                likes_val = metrics[0].text.strip() if len(metrics) > 0 else "0"
                comments_val = metrics[1].text.strip() if len(metrics) > 1 else "0"
                shares_val = metrics[2].text.strip() if len(metrics) > 2 else "0"
                
                posts_data.append({
                    "url": current_url,
                    "likes": likes_val,
                    "comments": comments_val,
                    "shares": shares_val
                })
                
            except Exception as e:
                print(f"  -> Error en la extracción del video {i+1}: Tiempo de espera agotado.")

            # Retornar al perfil principal para limpiar el contexto visual
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_selector('div[data-e2e="user-post-item"]', timeout=15000)
            await page.wait_for_timeout(1500)

        await browser.close()
        
    return posts_data

if __name__ == "__main__":
    test_user = "tiktok" 
    try:
        data = asyncio.run(get_recent_posts(test_user, limit=3)) 
        import json
        print("\nResultados:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\nError general de extracción: {e}")