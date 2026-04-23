import sys
import os
import json
import re
import requests
import webbrowser
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSpacerItem, 
                             QSizePolicy, QFrame, QTextEdit, QFileDialog, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont, QCursor

# ==========================================
# CONFIGURAÇÕES DO GITHUB UPDATER
# ==========================================
GITHUB_REPO = "BrunoTaletti/GhostCookie"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_current_version():
    v_path = resource_path("version.txt")
    if os.path.exists(v_path):
        with open(v_path, "r") as f:
            return f.read().strip()
    return "0.0.1"

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)

    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")
                release_url = data.get("html_url", "")
                
                current = get_current_version()
                curr_parts = [int(x) for x in current.split('.') if x.isdigit()]
                lat_parts = [int(x) for x in latest_version.split('.') if x.isdigit()]
                
                if lat_parts > curr_parts:
                    self.update_available.emit(latest_version, release_url)
        except Exception:
            pass 

class GhostCookie(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_version = get_current_version()
        self.update_url = None
        self.old_pos = None

        # Paleta Monocromática GhostCore
        self.color_success = "#FFFFFF" # Branco puro
        self.color_warning = "#888888" # Cinza médio
        self.color_error   = "#555555" # Cinza escuro (estilo ERR_SYS)
        self.color_base    = "#333333" # Borda padrão
        self.color_accent  = "#ffc31d" # Amarelo Ghost

        # Controle do Timer de Toasts
        self.toast_timer = QTimer()
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.clear_toast)

        self.init_ui()

        self.update_thread = UpdateChecker()
        self.update_thread.update_available.connect(self.on_update_available)
        self.update_thread.start()

    def init_ui(self):
        # Configuração Frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(resource_path("app-icon.ico")))
        self.resize(340, 500)

        # Container Principal
        self.central_widget = QFrame()
        self.central_widget.setObjectName("MainFrame")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # ==================== ESTILO GLOBAL E SCROLLBARS ====================
        self.setStyleSheet(f"""
            QFrame#MainFrame {{
                background-color: #000000;
                border: 1px solid {self.color_accent};
                border-top: 2px solid {self.color_accent};
            }}
            QLabel {{ color: #888888; font-family: 'Consolas', 'Segoe UI'; font-size: 11px; letter-spacing: 1px;}}
            
            /* Scrollbar Vertical Fininha (Cyberpunk Style) */
            QScrollBar:vertical {{
                border: none;
                background-color: #000000;
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #333333;
                min-height: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.color_accent};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            /* Botões de Ação do Grid */
            QPushButton.ActionBtn {{
                background-color: transparent; 
                border: 1px solid #333333; 
                color: #AAAAAA; 
                font-family: 'Consolas'; 
                font-size: 11px; 
                letter-spacing: 1px;
                padding: 8px;
            }}
            QPushButton.ActionBtn:hover {{ 
                background-color: #111111; 
                border: 1px solid #FFFFFF; 
                color: #FFFFFF; 
            }}
            
            /* Botão Exportar */
            QPushButton.ExportBtn {{
                background-color: #111111; 
                border: 1px solid #555555; 
                color: #FFFFFF; 
                font-family: 'Consolas'; 
                font-size: 12px; 
                font-weight: bold;
                letter-spacing: 2px;
                padding: 10px;
            }}
            QPushButton.ExportBtn:hover {{ background-color: #FFFFFF; color: #000000; }}

            /* Botão Inline de Limpar (SYS.CLR) */
            QPushButton.HeaderBtn {{
                background-color: transparent; 
                border: none; 
                color: #555555; 
                font-family: 'Consolas'; 
                font-size: 10px; 
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton.HeaderBtn:hover {{ color: {self.color_accent}; }}

            /* Botões do Top Bar */
            QPushButton#CloseBtn, QPushButton#MinBtn {{
                background-color: transparent; color: #555555; font-weight: bold; font-family: 'Consolas'; font-size: 14px;
            }}
            QPushButton#CloseBtn:hover, QPushButton#MinBtn:hover {{ color: #FFFFFF; }}
            
            /* Botão de Versão */
            QPushButton#VersionBtn {{
                background-color: transparent; border: none; color: #444444; font-size: 10px; font-family: 'Consolas'; letter-spacing: 1px;
                padding-top: 8px; padding-bottom: 5px;
            }}
            QPushButton#VersionBtn:hover {{ color: #FFFFFF; }}
            QPushButton#VersionBtnUpdate {{
                background-color: transparent; border: none; color: #FFFFFF; font-size: 10px; font-family: 'Consolas'; font-weight: bold;
                padding-top: 8px; padding-bottom: 5px;
            }}
            QPushButton#VersionBtnUpdate:hover {{ color: #AAAAAA; }}
        """)

        # 1. Custom Title Bar
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: #000000;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        
        title_label = QLabel("GHOST//COOKIE")
        title_label.setStyleSheet(f"color: {self.color_accent}; font-weight: bold; font-size: 11px; letter-spacing: 2px;")
        
        min_btn = QPushButton("—")
        min_btn.setObjectName("MinBtn")
        min_btn.setFixedSize(30, 30)
        min_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        min_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(min_btn)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)

        # 2. Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(8)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path("app-logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(220, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("GHOST//COOKIE")
            self.logo_label.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; font-family: 'Segoe UI';")
        content_layout.addWidget(self.logo_label)

        # Toast Feedback Label
        self.toast_label = QLabel("SYS_STANDBY //")
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.setContentsMargins(0, 8, 0, 8) 
        self.toast_label.setStyleSheet(f"color: {self.color_warning}; font-weight: bold; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
        content_layout.addWidget(self.toast_label)

        # Header do Input Stream (Layout horizontal para o texto e o botão de limpar)
        input_header_layout = QHBoxLayout()
        input_header_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_in = QLabel("INPUT_STREAM //")
        input_header_layout.addWidget(lbl_in)
        
        input_header_layout.addStretch() # Empurra o botão pra direita
        
        self.btn_clear = QPushButton("[ SYS.CLR ]")
        self.btn_clear.setProperty("class", "HeaderBtn")
        self.btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear.clicked.connect(self.limpar)
        input_header_layout.addWidget(self.btn_clear)
        
        content_layout.addLayout(input_header_layout)

        # Campo de Input
        self.input_text = QTextEdit()
        self.input_text.setAcceptRichText(False)
        self.input_text.setStyleSheet(self.get_textedit_style(self.color_base))
        self.input_text.textChanged.connect(self.realtime_validate)
        content_layout.addWidget(self.input_text)

        # Campo de Output
        lbl_out = QLabel("OUTPUT_STREAM //")
        content_layout.addWidget(lbl_out)

        self.output_text = QTextEdit()
        self.output_text.setAcceptRichText(False)
        self.output_text.setStyleSheet(self.get_textedit_style(self.color_base))
        self.output_text.setReadOnly(True) 
        content_layout.addWidget(self.output_text)

        # Grid de Botões Principais
        btn_grid = QGridLayout()
        btn_grid.setSpacing(6)

        self.btn_org = QPushButton("SYS.ORG")
        self.btn_org.setProperty("class", "ActionBtn")
        self.btn_org.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_org.clicked.connect(self.organizar)
        btn_grid.addWidget(self.btn_org, 0, 0)

        self.btn_val = QPushButton("SYS.VAL")
        self.btn_val.setProperty("class", "ActionBtn")
        self.btn_val.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_val.clicked.connect(self.validar)
        btn_grid.addWidget(self.btn_val, 0, 1)

        self.btn_min = QPushButton("SYS.MIN")
        self.btn_min.setProperty("class", "ActionBtn")
        self.btn_min.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_min.clicked.connect(self.minify)
        btn_grid.addWidget(self.btn_min, 1, 0)

        self.btn_copy = QPushButton("SYS.CPY")
        self.btn_copy.setProperty("class", "ActionBtn")
        self.btn_copy.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_copy.clicked.connect(self.copiar)
        btn_grid.addWidget(self.btn_copy, 1, 1)

        self.btn_exp = QPushButton("SYS.EXPORT")
        self.btn_exp.setProperty("class", "ExportBtn")
        self.btn_exp.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_exp.clicked.connect(self.exportar)
        btn_grid.addWidget(self.btn_exp, 2, 0, 1, 2)

        content_layout.addLayout(btn_grid)

        content_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Version Button
        self.version_btn = QPushButton(f"SYS.VER // {self.current_version}")
        self.version_btn.setObjectName("VersionBtn")
        self.version_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.version_btn.clicked.connect(self.handle_version_click)
        content_layout.addWidget(self.version_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(content_widget)

    # ==========================================
    # LÓGICA DE ARRASTAR A JANELA FRAMELESS
    # ==========================================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # ==========================================
    # STYLESHEET DINÂMICO DOS INPUTS
    # ==========================================
    def get_textedit_style(self, border_color):
        return f"""
            QTextEdit {{
                background-color: #050505; 
                border: 1px solid #111111;
                border-bottom: 2px solid {border_color};
                padding: 10px; 
                font-family: 'Consolas';
                font-size: 11px; 
                color: {self.color_success};
            }}
            QTextEdit:focus {{ border-bottom: 2px solid #FFFFFF; background-color: #0A0A0A; }}
        """

    # ==========================================
    # LÓGICA CORE & VALIDAÇÃO REAL-TIME
    # ==========================================
    def realtime_validate(self):
        text = self.input_text.toPlainText().strip()
        
        self.toast_timer.stop() 

        if not text:
            self.toast_label.setText("SYS_STANDBY //")
            self.toast_label.setStyleSheet(f"color: {self.color_warning}; font-weight: bold; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
            self.input_text.setStyleSheet(self.get_textedit_style(self.color_base))
            return
            
        try:
            parsed = json.loads(text)
            if isinstance(parsed, (dict, list)):
                self.toast_label.setText("SYS_OK // SINTAXE_VALIDA")
                self.toast_label.setStyleSheet(f"color: {self.color_success}; font-weight: bold; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
                self.input_text.setStyleSheet(self.get_textedit_style(self.color_success))
            else:
                raise ValueError()
        except (json.JSONDecodeError, ValueError):
            self.toast_label.setText("ERR_SYS // SINTAXE_INVALIDA")
            self.toast_label.setStyleSheet(f"color: {self.color_error}; font-weight: bold; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
            self.input_text.setStyleSheet(self.get_textedit_style(self.color_error))

    def limpar(self):
        self.input_text.clear()
        self.output_text.clear()
        self._set_output("", self.color_base)
        self.show_action_toast("SYS_OK // BUFFERS_LIMPOS", self.color_success)

    def organizar(self):
        text = self.input_text.toPlainText().strip()
        if not text: 
            self.show_action_toast("ERR_SYS // INPUT_VAZIO", self.color_error)
            return
            
        text = re.sub(r'\]\s*\[', ',', text)
        text = re.sub(r'\}\s*\{', '}, {', text)
        text = re.sub(r',\s*([\]}])', r'\1', text)
        if text.startswith("{") and text.endswith("}") and "},{" in text.replace(" ", ""):
            text = f"[{text}]"
            
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("OBJ_NOT_FOUND")
                
            pretty_json = json.dumps(parsed, indent=4)
            self._set_output(pretty_json, self.color_success)
            self.show_action_toast("SYS_OK // FORMATACAO_APLICADA", self.color_success)
        except (json.JSONDecodeError, ValueError) as e:
            error_msg = str(e).upper()
            self._set_output(f"// TRACE_DUMP:\n{error_msg}\n\n// RAW_BUFFER:\n{text}", self.color_error)
            self.show_action_toast("ERR_SYS // REVISAO_NECESSARIA", self.color_error)

    def validar(self):
        text = self.get_working_text()
        if not text:
            self.show_action_toast("ERR_SYS // INPUT_VAZIO", self.color_error)
            return
            
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("FORMAT_ERR")
                
            pretty_json = json.dumps(parsed, indent=4)
            self._set_output(pretty_json, self.color_success)
            self.show_action_toast("SYS_OK // SINTAXE_VALIDADA", self.color_success)
        except (json.JSONDecodeError, ValueError) as e:
            error_msg = str(e).upper()
            self._set_output(f"// TRACE_DUMP:\n{error_msg}\n\n// RAW_BUFFER:\n{text}", self.color_error)
            self.show_action_toast("ERR_SYS // FALHA_NA_VALIDACAO", self.color_error)

    def minify(self):
        text = self.get_working_text()
        if not text: 
            self.show_action_toast("ERR_SYS // DATA_NOT_FOUND", self.color_error)
            return
            
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, (dict, list)):
                raise ValueError("FORMAT_ERR")
                
            minified_json = json.dumps(parsed, separators=(',', ':'))
            self._set_output(minified_json, self.color_success)
            self.show_action_toast("SYS_OK // MINIFY_EXECUTADO", self.color_success)
        except (json.JSONDecodeError, ValueError):
            self.show_action_toast("ERR_SYS // SINTAXE_CORROMPIDA", self.color_error)

    def copiar(self):
        text = self.output_text.toPlainText().strip()
        if text and not text.startswith("// TRACE_DUMP"):
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.show_action_toast("SYS_OK // DADOS_COPIADOS", self.color_success)
        else:
            self.show_action_toast("ERR_SYS // CLIPBOARD_VAZIO", self.color_error)

    def exportar(self):
        text = self.output_text.toPlainText().strip()
        if text and not text.startswith("// TRACE_DUMP"):
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Exportar Buffer", "", "JSON Files (*.json);;Text Files (*.txt)"
            )
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.show_action_toast("SYS_OK // EXPORT_CONCLUIDO", self.color_success)
        else:
            self.show_action_toast("ERR_SYS // PAYLOAD_INVALIDO", self.color_error)

    def get_working_text(self):
        out_text = self.output_text.toPlainText().strip()
        if out_text and not out_text.startswith("// TRACE_DUMP"):
            return out_text
        return self.input_text.toPlainText().strip()

    def _set_output(self, text, border_color):
        self.output_text.setPlainText(text)
        self.output_text.setStyleSheet(self.get_textedit_style(border_color))

    # ==========================================
    # SISTEMA DE NOTIFICAÇÕES (TOAST)
    # ==========================================
    def show_action_toast(self, message, color):
        self.toast_label.setText(message)
        self.toast_label.setStyleSheet(f"color: {color}; font-weight: bold; font-family: 'Consolas'; font-size: 10px; letter-spacing: 1px;")
        self.toast_timer.start(2500) 

    def clear_toast(self):
        self.realtime_validate()

    # ==========================================
    # LÓGICA DE UPDATE
    # ==========================================
    def on_update_available(self, version, url):
        self.update_url = url
        self.version_btn.setText(f"UPDATE_READY // v{version}")
        self.version_btn.setObjectName("VersionBtnUpdate")
        self.version_btn.style().unpolish(self.version_btn)
        self.version_btn.style().polish(self.version_btn)

    def handle_version_click(self):
        if self.update_url:
            webbrowser.open(self.update_url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GhostCookie()
    window.show()
    sys.exit(app.exec())