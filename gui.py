import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
import json
import os
from src.main import run_pipeline

class TikTokScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Scraper Pro")
        self.root.geometry("600x550")
        self.root.configure(padx=20, pady=20)

        # Panel de entrada
        tk.Label(root, text="Ingresa el Username de TikTok (ej. @tiktok):", font=("Arial", 12, "bold")).pack(anchor="w")
        self.entry_user = tk.Entry(root, font=("Arial", 14))
        self.entry_user.pack(fill="x", pady=(5, 15))

        self.btn_run = tk.Button(root, text="▶ Extraer Datos", bg="#20D5EC", font=("Arial", 12, "bold"), command=self.start_scraping)
        self.btn_run.pack(fill="x", ipady=5)

        # Panel de visualización de datos
        tk.Label(root, text="Resultados:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 5))
        self.result_box = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", wrap=tk.WORD)
        self.result_box.pack(fill="both", expand=True)

    def start_scraping(self):
        username = self.entry_user.get().strip()
        if not username:
            messagebox.showwarning("Aviso", "El campo del usuario no puede estar vacío.")
            return

        # Bloquear botón y limpiar pantalla
        self.btn_run.config(state=tk.DISABLED, text="⏳ Extrayendo...")
        self.result_box.delete(1.0, tk.END)
        self.insert_text(f"Iniciando proceso para {username}...\n(El navegador invisible se está ejecutando de fondo)\n\n")

        # Ejecutar en un hilo separado para no congelar la interfaz
        threading.Thread(target=self.run_async_task, args=(username,), daemon=True).start()

    def run_async_task(self, username):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Ejecutamos el scraper y capturamos la ruta del JSON generado
            report_path = loop.run_until_complete(run_pipeline(username))

            if report_path and os.path.exists(report_path):
                self.display_json_data(report_path)
            else:
                self.insert_text("[ERROR] No se pudo generar el reporte JSON.\n")
        except Exception as e:
            self.insert_text(f"\n[ERROR CRÍTICO] {e}\n")
        finally:
            # Restaurar botón al terminar
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL, text="▶ Extraer Datos"))

    def display_json_data(self, filepath):
        """Lee el JSON y lo muestra estructurado en la interfaz."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        res = "="*50 + "\n"
        res += f" 👤 PERFIL: {data.get('username')}\n"
        res += "="*50 + "\n"
        res += f" 👥 Seguidores:  {data.get('followers')}\n"
        res += f" 👣 Siguiendo:   {data.get('following')}\n"
        res += f" ❤️ Likes Total: {data.get('total_likes')}\n"
        res += f" 📝 Bio:         {data.get('bio')}\n"
        res += "-"*50 + "\n"
        res += " 🎬 ÚLTIMAS PUBLICACIONES:\n"
        res += "-"*50 + "\n"

        for i, post in enumerate(data.get('recent_posts', [])):
            res += f"  Video {i+1}:\n"
            res += f"  🔗 URL:   {post.get('url')}\n"
            res += f"  👍 Likes: {post.get('likes')} | 💬 Coment: {post.get('comments')} | ⭐ Favs: {post.get('favorites')}\n\n"

        self.insert_text(res)

    def insert_text(self, text):
        """Inserta texto de forma segura desde el hilo secundario al principal."""
        self.root.after(0, self._append, text)

    def _append(self, text):
        # LÍNEAS CORREGIDAS: Únicamente result_box
        self.result_box.insert(tk.END, text)
        self.result_box.see(tk.END)

if __name__ == "__main__":
    ventana = tk.Tk()
    app = TikTokScraperGUI(ventana)
    ventana.mainloop()