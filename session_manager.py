import asyncio
from playwright.async_api import async_playwright

# Archivo donde se guardarán las credenciales y cookies
COOKIE_PATH = "tiktok_cookies.json"

async def generate_session():
    print("Iniciando navegador para captura de sesión...")
    async with async_playwright() as p:
        # headless=False es vital aquí para poder interactuar manualmente
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
        
        print("\n" + "=" * 50)
        print("TIENES 45 SEGUNDOS PARA:")
        print("1. Aceptar banners de cookies si aparecen.")
        print("2. Resolver CAPTCHA si aparece.")
        print("3. Hacer scroll leve en la página simulando ser humano.")
        print("=" * 50 + "\n")

        # Tiempo de espera para la interacción manual
        await page.wait_for_timeout(45000)
        
        # Guarda el estado (cookies, tokens)
        await context.storage_state(path=COOKIE_PATH)
        print(f"\n[+] Sesión guardada exitosamente en: {COOKIE_PATH}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(generate_session())