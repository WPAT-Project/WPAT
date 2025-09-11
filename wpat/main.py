# -*- coding: utf-8 -*-

import os
import sys
import re
import signal
import datetime
import argparse
import requests
from urllib.parse import urlparse
from time import sleep
from colorama import Fore, Style, init
from contextlib import redirect_stdout
from wpat.scripts import (
    check_user_enumeration,
    check_xmlrpc,
    scan_sensitive_files,
    detect_wp_version,
    check_rest_api,
    scan_plugins,
    generate_wordlists,
    scan_themes,
    brute_force,
    check_ssl,
    check_security_txt,
    scan_cors,
    generate_report,
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
    "9": {"name": "Verificar Certificado SSL", "func": check_ssl, "full": True},
    "10": {"name": "Verificar Security.txt", "func": check_security_txt, "full": True},
    "11": {"name": "Verificar CORS", "func": scan_cors, "full": True},
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
{Fore.CYAN}          Versión 2.1 · Ethical Hacking
{Fore.YELLOW}         Creado por Santitub | {Fore.BLUE}https://github.com/Santitub
{Fore.MAGENTA}─────────────────────────────────────────────
{Style.RESET_ALL}"""
    print(banner)

def check_url(url):
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        print(f"\n{Fore.RED}[!] URL no válida: {url}")
        sleep(1)
        return False

    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code >= 400:
            print(f"\n{Fore.RED}[!] La URL respondió con un error HTTP: {response.status_code}")
            sleep(1)
            return False
    except requests.RequestException as e:
        print(f"\n{Fore.RED}[!] Error de conexión con la URL: {e}")
        sleep(3)
        return False

    return True

def get_target_url():
    while True:
        clear_console()
        print_banner()
        print(f"{Style.BRIGHT}{Fore.MAGENTA}►► {Fore.CYAN}PASO 1/3: {Fore.WHITE}CONFIGURACIÓN INICIAL")
        url = input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL objetivo {Fore.YELLOW}(ej: https://ejemplo.com){Fore.WHITE}: ").strip().rstrip('/')
        
        if check_url(url):
            return url

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
    html_file = os.path.splitext(log_file)[0] + ".html"

    with open(log_file, 'w', encoding="utf-8") as f:
        dual = DualOutput(sys.stdout, f)
        with redirect_stdout(dual):
            if choice == '97':  # Auditoría Completa
                print(f"{Style.BRIGHT}{Fore.CYAN}► {Fore.WHITE}Ejecutando auditoría completa...\n")
                for key in [k for k, v in TOOLS.items() if v['full']]:
                    print(f"{Fore.MAGENTA}════════════ {TOOLS[key]['name'].upper()} {Fore.MAGENTA}════════════")
                    TOOLS[key]['func'](url)
                    print()
                # Llamar al método generate_report al final
                generate_report(log_file)
                print(f"\n{Style.BRIGHT}{Fore.GREEN}✓ {Fore.WHITE}Log HTML guardado en: {Fore.YELLOW}{html_file}")
            else:
                TOOLS[choice]['func'](url)

    print(f"\n{Style.BRIGHT}{Fore.GREEN}✓ {Fore.WHITE}Log guardado en: {Fore.YELLOW}{log_file}")

def main():
    parser = argparse.ArgumentParser(description='WordPress Professional Audit Tool')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI version')
    args = parser.parse_args()

    if args.gui:
        os.system(f"{sys.executable} -m wpat.gui")
        return

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
                sleep(1)
        else:
            print(f"\n{Fore.RED}⚠ Opción inválida{Style.RESET_ALL}")
            sleep(1)

if __name__ == "__main__":
    main()
