import os
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

COOKIE_PATH = "tiktok_cookies.json"

async def get_recent_posts(username: str, limit: int = 5) -> list:
    clean_username = username if username.startswith("@") else f"@{username}"
    target_url = f"https://www.tiktok.com/{clean_username}"

    if not os.path.exists(COOKIE_PATH):
        raise FileNotFoundError(f"Archivo de sesión '{COOKIE_PATH}' no encontrado.")

    posts_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=COOKIE_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(target_url, wait_until="domcontentloaded")
        
        try:
            # 60 segundos de paciencia para cargar
            await page.wait_for_selector('div[data-e2e="user-post-item"]', timeout=60000)
            await page.wait_for_timeout(2000) 
        except Exception as e:
            # CORRECCIÓN: variable 'e' declarada correctamente
            print(f"[ALERTA] No se encontró la cuadrícula de videos. Error: {e}")
            await browser.close()
            return posts_data

        video_count = await page.locator('div[data-e2e="user-post-item"]').count()
        actual_limit = min(limit, video_count)

        if actual_limit == 0:
            await browser.close()
            return posts_data

        for i in range(actual_limit):
            try:
                # Clic en miniatura
                await page.locator('div[data-e2e="user-post-item"] a').nth(i).click()
                
                # Buscar selectores del modal de video emergente
                await page.wait_for_selector('strong[data-e2e="browse-like-count"]', timeout=15000)
                await page.wait_for_timeout(1000) 
                
                current_url = page.url
                post_html = await page.content()
                post_soup = BeautifulSoup(post_html, "html.parser")

                like_btn = post_soup.find("strong", {"data-e2e": "browse-like-count"})
                comment_btn = post_soup.find("strong", {"data-e2e": "browse-comment-count"})
                fav_btn = post_soup.find("strong", {"data-e2e": "browse-favorite-count"})
                
                posts_data.append({
                    "url": current_url,
                    "likes": like_btn.text.strip() if like_btn else "0",
                    "comments": comment_btn.text.strip() if comment_btn else "0",
                    "favorites": fav_btn.text.strip() if fav_btn else "0"
                })
                
            except Exception as e:
                print(f"  -> Error en la extracción del video {i+1}: {e}")

            # Recargar perfil para limpiar el modal
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_selector('div[data-e2e="user-post-item"]', timeout=15000)
            await page.wait_for_timeout(1500)

        await browser.close()
        
    return posts_data