import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget,
                             QFrame, QScrollArea, QMessageBox, QAction)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt, QUrl
from PyQt5.QtGui import QTextCursor, QFont, QCloseEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# Importar herramientas
from wpat.scripts import (
    check_user_enumeration_gui,
    check_xmlrpc,
    scan_sensitive_files,
    detect_wp_version,
    check_rest_api,
    scan_plugins_gui,
    scan_themes_gui,
    brute_force,
    check_ssl,
    generate_wordlists_gui,
    check_security_txt
)

# Configuración de herramientas
TOOLS = {
    "1": {"name": "Detectar Enumeración de Usuarios", "func": check_user_enumeration_gui, "full": True},
    "2": {"name": "Analizar XML-RPC", "func": check_xmlrpc, "full": True},
    "3": {"name": "Escáner de Archivos Sensibles", "func": scan_sensitive_files, "full": True},
    "4": {"name": "Detectar Versión de WordPress", "func": detect_wp_version, "full": True},
    "5": {"name": "Auditar REST API", "func": check_rest_api, "full": True},
    "6": {"name": "Escáner de Plugins", "func": scan_plugins_gui, "full": False, "input": True},
    "7": {"name": "Escáner de Temas", "func": scan_themes_gui, "full": False, "input": True},    
    "8": {"name": "Fuerza Bruta en Login", "func": brute_force, "full": False, "input": True},
    "9": {"name": "Verificar Certificado SSL", "func": check_ssl, "full": True},
    "10": {"name": "Verificar Security.txt", "func": check_security_txt, "full": True},
    "98": {"name": "Actualizar Wordlists", "func": generate_wordlists_gui, "full": False, "color": "#f39c12"}
}

STYLES = {
    'dark': {
        'background': '#2D2D2D',
        'foreground': '#FFFFFF',
        'primary': '#3498DB',
        'disabled': '#606060',
        'input_bg': '#404040',
        'input_fg': '#FFFFFF'
    },
    'light': {
        'background': '#F5F6FA',
        'foreground': '#2D2D2D',
        'primary': '#2980B9',
        'disabled': '#A0A0A0',
        'input_bg': '#FFFFFF',
        'input_fg': '#000000'
    }
}

class WebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok):
        if ok:
            self.runJavaScript("document.documentElement.outerHTML")

class OutputEmitter(QObject):
    new_output = pyqtSignal(str)

    def write(self, text):
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        self.new_output.emit(clean_text)

    def flush(self):
        pass

class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, func, url, extra_arg=None):
        super().__init__()
        self.func = func
        self.url = url
        self.extra_arg = extra_arg
        self._is_running = True

    def run(self):
        try:
            if self.extra_arg:
                self.func(self.url, self.extra_arg)
            else:
                self.func(self.url)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait()

class WordPressAuditorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.current_url = None
        self.log_dir = "logs"
        self.tool_buttons = []
        self.audit_queue = []
        self.current_worker = None
        os.makedirs(self.log_dir, exist_ok=True)
        self.initUI()
        self.setup_output_redirection()
        self.update_button_states()
        self.apply_theme()

    def initUI(self):
        self.setWindowTitle("WPAT-GUI")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_menu()
        self.setup_main_tabs()

    def setup_menu(self):
        menu_bar = self.menuBar()
        theme_menu = menu_bar.addMenu('&Tema')
        toggle_action = QAction('Cambiar Tema', self)
        toggle_action.triggered.connect(self.toggle_theme)
        theme_menu.addAction(toggle_action)

    def setup_main_tabs(self):
        main_tabs = QTabWidget()
        main_tabs.addTab(self.create_url_tab(), "URL")
        main_tabs.addTab(self.create_tools_tab(), "Herramientas")
        main_tabs.addTab(self.create_logs_tab(), "Logs")
        self.setCentralWidget(main_tabs)

    def create_url_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # URL Input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ingrese la URL del sitio WordPress")
        self.load_url_btn = QPushButton("Cargar URL")
        self.load_url_btn.clicked.connect(self.load_url)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.load_url_btn)
        
        # Web Preview
        self.web_view = QWebEngineView()
        self.web_page = WebPage(self.web_view)
        
        layout.addLayout(url_layout)
        layout.addWidget(self.web_view)
        tab.setLayout(layout)
        return tab

    def create_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        content = QWidget()
        content_layout = QVBoxLayout(spacing=10)
        
        # Auditoría Completa
        self.full_audit_btn = QPushButton("AUDITORÍA COMPLETA")
        self.full_audit_btn.clicked.connect(self.start_full_audit)
        self.full_audit_btn.setObjectName("fullAuditButton")
        content_layout.addWidget(self.full_audit_btn)
        
        # Herramientas Automáticas
        content_layout.addWidget(QLabel("Herramientas Automáticas:"))
        for key in TOOLS:
            if TOOLS[key]["full"]:
                btn = self.create_tool_button(TOOLS[key])
                content_layout.addWidget(btn)
        
        # Herramientas Manuales
        content_layout.addWidget(QLabel("\nHerramientas Manuales:"))
        for key in TOOLS:
            if not TOOLS[key].get("full", False) and key != "98":
                btn = self.create_tool_button(TOOLS[key])
                content_layout.addWidget(btn)
        
        # Botón de Wordlists
        wordlist_btn = self.create_tool_button(TOOLS["98"])
        wordlist_btn.setObjectName("wordlistButton")
        content_layout.addWidget(wordlist_btn)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        tab.setLayout(layout)
        return tab

    def create_tool_button(self, tool):
        btn = QPushButton(tool["name"])
        if tool["func"]:
            btn.clicked.connect(lambda _, t=tool: self.run_tool(t["func"]))
        btn.setEnabled(False)
        self.tool_buttons.append(btn)
        return btn

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_output)
        tab.setLayout(layout)
        return tab

    def setup_output_redirection(self):
        self.output_emitter = OutputEmitter()
        self.output_emitter.new_output.connect(self.append_log)
        sys.stdout = self.output_emitter

    def apply_theme(self):
        style = STYLES[self.current_theme]
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {style['background']};
                color: {style['foreground']};
            }}
            QPushButton {{
                background-color: {style['primary']};
                color: white;
                padding: 8px;
                border-radius: 4px;
                min-width: 120px;
            }}
            QPushButton:disabled {{
                background-color: {style['disabled']};
                color: #909090;
            }}
            QPushButton#fullAuditButton {{
                background-color: #27ae60;
                font-weight: bold;
                padding: 12px;
            }}
            QPushButton#wordlistButton {{
                background-color: #f39c12;
            }}
            QLineEdit, QTextEdit {{
                background-color: {style['input_bg']};
                color: {style['input_fg']};
                border: 1px solid {style['primary']};
                padding: 6px;
            }}
        """)

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()

    def closeEvent(self, event):
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
        sys.stdout = sys.__stdout__
        event.accept()

    def load_url(self):
        url = self.url_input.text().strip().rstrip('/')
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Error", "URL debe comenzar con http:// o https://")
            return
        
        self.current_url = url
        self.web_view.load(QUrl(url))
        self.update_button_states()

    def update_button_states(self):
        enabled = self.current_url is not None
        for btn in self.tool_buttons:
            btn.setEnabled(enabled)
        self.full_audit_btn.setEnabled(enabled)

    def run_tool(self, func):
        if not self.current_url:
            return
            
        self.current_worker = Worker(func, self.current_url)
        self.current_worker.finished.connect(self.on_tool_finished)
        self.current_worker.error.connect(self.on_tool_error)
        self.current_worker.start()
        self.centralWidget().setCurrentIndex(2)

    def start_full_audit(self):
        if not self.current_url:
            return
        
        self.audit_queue = [tool["func"] for tool in TOOLS.values() if tool.get("full")]
        self.log_output.clear()
        self.run_next_audit()

    def run_next_audit(self):
        if self.audit_queue:
            tool = self.audit_queue.pop(0)
            self.run_tool(tool)

    def on_tool_finished(self):
        self.append_log("\nOperación completada\n")
        self.run_next_audit()

    def on_tool_error(self, error_msg):
        self.append_log(f"\nERROR: {error_msg}\n")
        self.run_next_audit()

    def append_log(self, text):
        self.log_output.moveCursor(QTextCursor.End)
        self.log_output.insertPlainText(text)
        self.log_output.ensureCursorVisible()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WordPressAuditorGUI()
    window.show()
    sys.exit(app.exec_())
