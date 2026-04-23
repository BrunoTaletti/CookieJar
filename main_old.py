import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import json
import re
from PIL import Image
import sys
import os
import requests
import threading
import webbrowser

# Tema minimalista (Força o dark mode nativo)
ctk.set_appearance_mode("dark")

def resource_path(relative_path):
    """ Retorna o caminho absoluto, essencial para o PyInstaller encontrar arquivos após o build """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CookieJarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CORES ---
        self.color_bg_dark = "#0E0E0E"
        self.color_bg_light = "#171717"
        self.color_text = "#FFFFFF"
        self.color_border = "#333333"
        
        self.color_success = "#00FF7F"
        self.color_error = "#FF4C4C"
        self.color_warning = "#FFCC00"

        # --- CONFIGURAÇÃO DA JANELA ---
        self.title("CookieJar")
        self.geometry("380x560")
        self.minsize(320, 500) 
        self.configure(fg_color=self.color_bg_dark)
        
        # --- ÍCONE DA JANELA ---
        try:
            self.iconbitmap(resource_path("app-icon.ico"))
        except Exception:
            try:
                app_icon = tk.PhotoImage(file=resource_path("app-icon.png"))
                self.iconphoto(False, app_icon)
            except Exception:
                pass

        # --- LOGO / NOME DO APP ---
        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open(resource_path("app-logo.png")),
                dark_image=Image.open(resource_path("app-logo.png")),
                size=(300, 120) 
            )
            self.title_label = ctk.CTkLabel(self, image=logo_img, text="")
        except Exception:
            self.title_label = ctk.CTkLabel(
                self, text="CookieJar 👻", font=("Segoe UI", 24, "bold"), text_color=self.color_text
            )
        self.title_label.pack(pady=(15, 5))

        # --- CAMPOS DE TEXTO ---
        self.input_label = ctk.CTkLabel(self, text="JSON(s) de entrada:", font=("Segoe UI", 12, "bold"), text_color=self.color_text)
        self.input_label.pack(anchor="w", padx=15)
        
        self.input_text = ctk.CTkTextbox(self, height=80, font=("Consolas", 12), fg_color=self.color_bg_light, border_color=self.color_border, border_width=1, text_color=self.color_text)
        self.input_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.output_label = ctk.CTkLabel(self, text="Resultado:", font=("Segoe UI", 12, "bold"), text_color=self.color_text)
        self.output_label.pack(anchor="w", padx=15)
        
        self.output_text = ctk.CTkTextbox(self, height=80, font=("Consolas", 12), fg_color=self.color_bg_light, border_color=self.color_border, border_width=1, text_color=self.color_text)
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # --- BOTÕES ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=5)
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)

        self.btn_org = ctk.CTkButton(self.btn_frame, text="🔄 Organizar", command=self.organizar, fg_color="#222222", hover_color="#444444", text_color=self.color_text, border_width=1, border_color="#555555")
        self.btn_org.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_val = ctk.CTkButton(self.btn_frame, text="🔍 Validar", command=self.validar, fg_color="#222222", hover_color="#444444", text_color=self.color_text, border_width=1, border_color="#555555")
        self.btn_val.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_min = ctk.CTkButton(self.btn_frame, text="🗜️ Minify", command=self.minify, fg_color="#222222", hover_color="#444444", text_color=self.color_text, border_width=1, border_color="#555555")
        self.btn_min.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_copy = ctk.CTkButton(self.btn_frame, text="📋 Copiar", command=self.copiar, fg_color="#222222", hover_color="#444444", text_color=self.color_text, border_width=1, border_color="#555555")
        self.btn_copy.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_exp = ctk.CTkButton(self.btn_frame, text="💾 Exportar", command=self.exportar, fg_color=self.color_text, hover_color="#CCCCCC", text_color="#000000", font=("Segoe UI", 13, "bold"))
        self.btn_exp.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")

        self.toast_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 13, "bold"))
        self.toast_label.pack(pady=2)

        # --- RODAPÉ E VERSÃO ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", pady=(0, 5))

        self.version = self.load_version()
        self.version_label = ctk.CTkLabel(self.footer_frame, text=f"v{self.version}", font=("Segoe UI", 10), text_color="#444444")
        self.version_label.pack(side="left", padx=5)

        # Botão de update (Oculto por padrão)
        self.btn_update = ctk.CTkButton(
            self.footer_frame, text="Atualizar app", fg_color="#0066CC", hover_color="#004C99", 
            font=("Segoe UI", 10, "bold"), width=90, height=20, command=self.open_update_link
        )
        
        # Inicia a checagem de update em background
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    # --- FUNÇÕES DE UPDATE ---
    def load_version(self):
        try:
            with open(resource_path("version.txt"), "r") as f:
                return f.read().strip()
        except Exception:
            return "0.0.1"

    def check_for_updates(self):
        try:
            UPDATE_TXT_URL = "https://raw.githubusercontent.com/brunotaletti/CookieJar/main/version.txt"
            
            response = requests.get(UPDATE_TXT_URL, timeout=5)
            if response.status_code == 200:
                latest_version = response.text.strip()
                if self.is_newer_version(self.version, latest_version):
                    # Traz a exibição do botão para a thread principal da interface
                    self.after(0, self.show_update_button)
        except Exception:
            # Falha silenciosa (sem internet, link off, etc)
            pass

    def is_newer_version(self, current, latest):
        try:
            # Converte "1.0.5" para [1, 0, 5] para comparar corretamente matematicamente
            curr_parts = [int(x) for x in current.split('.') if x.isdigit()]
            lat_parts = [int(x) for x in latest.split('.') if x.isdigit()]
            return lat_parts > curr_parts
        except Exception:
            return False

    def show_update_button(self):
        self.btn_update.pack(side="left", padx=5)

    def open_update_link(self):
        RELEASE_URL = "https://github.com/BrunoTaletti/CookieJar/releases/latest"
        webbrowser.open(RELEASE_URL)

    # --- LÓGICA CORE ---
    def organizar(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text: 
            self.show_toast("⚠️ Insira dados primeiro.", self.color_warning)
            return
            
        text = re.sub(r'\]\s*\[', ',', text)
        text = re.sub(r'\}\s*\{', '}, {', text)
        text = re.sub(r',\s*([\]}])', r'\1', text)
        if text.startswith("{") and text.endswith("}") and "},{" in text.replace(" ", ""):
            text = f"[{text}]"
            
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("JSON não é um objeto ou lista.")
                
            pretty_json = json.dumps(parsed, indent=4)
            self._set_output(pretty_json, self.color_success)
            self.show_toast("✨ Organizado e Corrigido!", self.color_success)
        except (json.JSONDecodeError, ValueError) as e:
            self._set_output(f"Ainda há erros:\n{str(e)}\n\nResultado parcial:\n{text}", self.color_warning)
            self.show_toast("⚠️ Requer revisão.", self.color_warning)

    def validar(self):
        text = self.get_working_text()
        if not text:
            self.show_toast("⚠️ Insira dados para validar.", self.color_warning)
            return
            
        try:
            parsed = json.loads(text)
            
            # Validação rigorosa: Garante que é uma estrutura JSON real (Dicionário ou Lista)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("O formato não é um objeto JSON {} ou array [].")
                
            pretty_json = json.dumps(parsed, indent=4)
            self._set_output(pretty_json, self.color_success)
            self.show_toast("✅ JSON Válido!", self.color_success)
        except (json.JSONDecodeError, ValueError) as e:
            self._set_output(f"❌ JSON Inválido:\n{str(e)}", self.color_error)
            self.show_toast("❌ Falha na validação", self.color_error)

    def minify(self):
        text = self.get_working_text()
        if not text: 
            self.show_toast("⚠️ Insira dados primeiro.", self.color_warning)
            return
            
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("Formato inválido.")
                
            minified_json = json.dumps(parsed, separators=(',', ':'))
            self._set_output(minified_json, self.color_success)
            self.show_toast("🗜️ Minificado!", self.color_text)
        except (json.JSONDecodeError, ValueError):
            self.show_toast("⚠️ Valide ou organize o JSON primeiro.", self.color_warning)

    def copiar(self):
        text = self.output_text.get("1.0", "end-1c").strip()
        if text and not text.startswith("❌") and not text.startswith("Ainda"):
            self.clipboard_clear()
            self.clipboard_append(text)
            self.show_toast("📋 Copiado!", self.color_text)
        else:
            self.show_toast("⚠️ Nada válido para copiar.", self.color_warning)

    def exportar(self):
        text = self.output_text.get("1.0", "end-1c").strip()
        if text and not text.startswith("❌") and not text.startswith("Ainda"):
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json")], title="Exportar"
            )
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.show_toast("💾 Exportado com sucesso!", self.color_success)
        else:
            self.show_toast("⚠️ Nada válido para exportar.", self.color_warning)

    def get_working_text(self):
        out_text = self.output_text.get("1.0", "end-1c").strip()
        if out_text and not out_text.startswith("❌") and not out_text.startswith("Ainda"):
            return out_text
        return self.input_text.get("1.0", "end-1c").strip()

    def _set_output(self, text, color):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(text_color=color)

    def show_toast(self, message, color):
        self.toast_label.configure(text=message, text_color=color)
        self.after(2500, lambda: self.toast_label.configure(text=""))

if __name__ == "__main__":
    app = CookieJarApp()
    app.mainloop()