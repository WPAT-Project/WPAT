import os
import sys
import re
import signal
import datetime
from colorama import Fore, Style, init
from contextlib import redirect_stdout
from scripts import (
    check_user_enumeration,
    check_xmlrpc,
    scan_sensitive_files,
    detect_wp_version,
    check_rest_api,
    scan_plugins,
    generate_wordlists,
    scan_themes,
    brute_force
)

init(autoreset=True)

def signal_handler(sig, frame):
    print(f"\n{Style.BRIGHT}{Fore.RED}✂ {Fore.WHITE}Auditoría interrumpida! Saliendo...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

TOOLS = {
    "1": {"name": "Detectar Enumeración de Usuarios", "func": check_user_enumeration, "full": True},
    "2": {"name": "Analizar XML-RPC", "func": check_xmlrpc, "full": True},
    "3": {"name": "Escáner de Archivos Sensibles", "func": scan_sensitive_files, "full": True},
    "4": {"name": "Detectar Versión de WordPress", "func": detect_wp_version, "full": True},
    "5": {"name": "Auditar REST API", "func": check_rest_api, "full": True},
    "6": {"name": "Escáner de Plugins", "func": scan_plugins, "full": False},
    "7": {"name": "Escáner de Temas", "func": scan_themes, "full": False},    
    "8": {"name": "Fuerza Bruta en Login", "func": brute_force, "full": False},
    "97": {"name": "Auditoría Completa", "func": None, "full": False},
    "98": {"name": "Actualizar Wordlists", "func": generate_wordlists, "full": False},
    "99": {"name": "Salir", "func": None, "full": False}
}

class DualOutput:
    def __init__(self, console, log_file):
        self.console = console
        self.log_file = log_file
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

    def write(self, text):
        self.console.write(text)
        self.log_file.write(self.ansi_escape.sub('', text))

    def flush(self):
        self.console.flush()
        self.log_file.flush()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Style.BRIGHT}{Fore.CYAN}
██╗    ██╗██████╗  █████╗ ████████╗
██║    ██║██╔══██╗██╔══██╗╚══██╔══╝
██║ █╗ ██║██████╔╝███████║   ██║   
██║███╗██║██╔═══╝ ██╔══██║   ██║   
╚███╔███╔╝██║     ██║  ██║   ██║   
 ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   
{Fore.MAGENTA}─────────────────────────────────────────────
{Fore.WHITE}       WordPress Professional Audit Tool
{Fore.CYAN}          Versión 1.2 · Ethical Hacking
{Fore.YELLOW}         Creado por Santitub | {Fore.BLUE}https://github.com/Santitub
{Fore.MAGENTA}─────────────────────────────────────────────
{Style.RESET_ALL}"""
    print(banner)

def get_target_url():
    print(f"{Style.BRIGHT}{Fore.MAGENTA}►► {Fore.CYAN}PASO 1/3: {Fore.WHITE}CONFIGURACIÓN INICIAL")
    return input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL objetivo {Fore.YELLOW}(ej: https://ejemplo.com){Fore.WHITE}: ").strip().rstrip('/')

def print_menu(url):
    clear_console()
    print(f"""
{Style.BRIGHT}{Fore.MAGENTA}►► {Fore.CYAN}PASO 2/3: {Fore.WHITE}MENÚ PRINCIPAL
{Fore.MAGENTA}═══════════════════════════════════════════════
{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Objetivo: {Fore.YELLOW}{url}
""")
    for key in sorted(TOOLS.keys(), key=int):
        tool = TOOLS[key]
        print(f"{Style.BRIGHT}{Fore.CYAN} [{Fore.MAGENTA}{key}{Fore.CYAN}] {Fore.WHITE}{tool['name']}")
    print(f"{Fore.MAGENTA}═══════════════════════════════════════════════""")

def run_tool(url, choice):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    log_file = os.path.join(log_dir, f"auditoria_{timestamp}.txt")

    with open(log_file, 'w') as f:
        dual = DualOutput(sys.stdout, f)
        with redirect_stdout(dual):
            if choice == '97':  # Auditoría Completa
                print(f"{Style.BRIGHT}{Fore.CYAN}► {Fore.WHITE}Ejecutando auditoría completa...\n")
                for key in [k for k, v in TOOLS.items() if v['full']]:
                    print(f"{Fore.MAGENTA}════════════ {TOOLS[key]['name'].upper()} {Fore.MAGENTA}════════════")
                    TOOLS[key]['func'](url)
                    print()
            else:
                TOOLS[choice]['func'](url)

    print(f"\n{Style.BRIGHT}{Fore.GREEN}✓ {Fore.WHITE}Log guardado en: {Fore.YELLOW}{log_file}")

def main():
    print_banner()
    url = get_target_url()
    
    while True:
        print_menu(url)
        choice = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Selección {Fore.YELLOW}(1-99){Fore.WHITE}: ").strip()

        if choice == '99':
            print(f"\n{Style.BRIGHT}{Fore.CYAN}► {Fore.MAGENTA}¡Auditoría finalizada! {Fore.YELLOW}\n")
            break
            
        if choice in TOOLS:
            if choice in ['97', '98']:  # Opciones especiales
                clear_console()
                run_tool(url, choice)
                input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Presiona Enter para continuar...")
            elif TOOLS[choice]['func']:
                clear_console()
                run_tool(url, choice)
                input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Presiona Enter para continuar...")
            else:
                print(f"\n{Fore.RED}⚠ Opción sin funcionalidad asignada{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}⚠ Opción inválida{Style.RESET_ALL}")

if __name__ == "__main__":
    main()