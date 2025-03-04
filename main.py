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
    scan_plugins
)

init(autoreset=True)

def signal_handler(sig, frame):
    print(f"\n{Style.BRIGHT}{Fore.RED}❌ Auditoría interrumpida! {Fore.WHITE}Saliendo...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

TOOLS = {
    "1": {"name": "Detectar Enumeración de Usuarios", "func": check_user_enumeration},
    "2": {"name": "Analizar XML-RPC", "func": check_xmlrpc},
    "3": {"name": "Escáner de Archivos Sensibles", "func": scan_sensitive_files},
    "4": {"name": "Detectar Versión de WordPress", "func": detect_wp_version},
    "5": {"name": "Auditar REST API", "func": check_rest_api},
    "6": {"name": "Escáner de Plugins", "func": scan_plugins},
    "7": {"name": "Auditoría Completa", "func": None},
    "8": {"name": "Salir", "func": None}
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
{Fore.CYAN}          Versión 1.1 · Ethical Hacking
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
{Fore.MAGENTA}─────────────────────────────────────────────
{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Objetivo: {Fore.YELLOW}{url}
""")
    for key in TOOLS:
        print(f"{Style.BRIGHT}{Fore.CYAN} [{Fore.MAGENTA}{key}{Fore.CYAN}] {Fore.WHITE}{TOOLS[key]['name']}")
    print(f"{Fore.MAGENTA}─────────────────────────────────────────────")

def run_tool(url, choice):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    log_file = os.path.join(log_dir, f"auditoria_{timestamp}.txt")

    with open(log_file, 'w') as f:
        dual = DualOutput(sys.stdout, f)
        with redirect_stdout(dual):
            if choice == '7':
                print(f"{Style.BRIGHT}{Fore.CYAN}► {Fore.WHITE}Ejecutando auditoría completa... {Fore.YELLOW}🛡️\n")
                for key in [k for k in TOOLS if k not in ("6", "7", "8")]:
                    print(f"{Fore.MAGENTA}────── {TOOLS[key]['name'].upper()} {Fore.MAGENTA}──────")
                    TOOLS[key]['func'](url)
                    print()
            else:
                if TOOLS[choice]['func']:
                    TOOLS[choice]['func'](url)

    print(f"\n[✓] Log guardado en: {log_file}")

def main():
    print_banner()
    url = get_target_url()
    
    while True:
        print_menu(url)
        choice = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Selección {Fore.YELLOW}(1-8){Fore.WHITE}: ").strip()

        if choice == '8':
            print(f"\n{Style.BRIGHT}{Fore.CYAN}► {Fore.MAGENTA}¡Auditoría finalizada! {Fore.YELLOW}🛡️\n")
            break
            
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            clear_console()
            run_tool(url, choice)
            input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Presiona Enter para continuar...")

if __name__ == "__main__":
    main()