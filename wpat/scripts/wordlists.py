import requests
import re
import sys
import signal
import os
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS WORDLIST GENERATOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

HEADERS = {
    'User-Agent': 'WP Audit Tool',
    'Accept-Language': 'en-US,en;q=0.5'
}

def signal_handler(sig, frame):
    print(f"\n{Fore.RED}✂️ {Fore.WHITE}Interrupción recibida. Saliendo...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_status(message, status="info"):
    status_colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    print(f"{Style.BRIGHT}{status_colors[status]}▶ {Fore.WHITE}{message}")

def fetch_items(url, item_type):
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.get, url, headers=HEADERS, timeout=20)
            response = future.result()
            
        response.raise_for_status()
        lines = response.text.splitlines()[4:]
        
        processed = []
        for line in lines:
            clean_line = re.sub(r'<[^>]*>|\s{2,}|/', '', line).strip()
            if clean_line and "Apache" not in clean_line:
                processed.append(clean_line)
                
        return sorted(set(processed)) if processed else None

    except requests.exceptions.HTTPError as e:
        print_status(f"Error HTTP {e.response.status_code}", "error")
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
    return None

def generate_wordlists(url=None):
    print(BANNER)
    print(f"{Fore.CYAN}► {Fore.WHITE}Selecciona qué listas generar:")
    print(f"{Fore.CYAN} 1 {Fore.WHITE}Plugins")
    print(f"{Fore.CYAN} 2 {Fore.WHITE}Temas")
    print(f"{Fore.CYAN} 3 {Fore.WHITE}Ambos\n")
    
    choice = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Opción (1-3): ").strip()
    
    targets = []
    if choice == '1':
        targets.append(('plugins', 'https://plugins.svn.wordpress.org/'))
    elif choice == '2':
        targets.append(('temas', 'https://themes.svn.wordpress.org/'))
    elif choice == '3':
        targets.extend([
            ('plugins', 'https://plugins.svn.wordpress.org/'),
            ('temas', 'https://themes.svn.wordpress.org/')
        ])
    else:
        print_status("Opción inválida", "error")
        return

    log_dir = "wordlists"
    os.makedirs(log_dir, exist_ok=True)

    for item_type, url in targets:
        items = fetch_items(url, item_type)
        if items:
            filename = os.path.join(log_dir, f"{item_type}.txt")
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(items))
                print_status(f"{len(items)} {item_type} guardados en {Fore.YELLOW}{filename}", "success")
            except Exception as e:
                print_status(f"Error guardando {item_type}: {str(e)}", "error")