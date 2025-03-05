import requests
import time
import signal
import sys
from random import uniform
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS THEME SCANNER {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

shutdown = False

def handle_sigint(signum, frame):
    global shutdown
    if not shutdown:
        shutdown = True
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Escaneo cancelado")
        sys.exit(1)

signal.signal(signal.SIGINT, handle_sigint)

def check_theme(target_url, theme, timeout=15):
    global shutdown
    if shutdown:
        return ("cancelled", None)
    
    headers = {'User-Agent': 'WP Audit Tool'}
    url = f"{target_url.rstrip('/')}/wp-content/themes/{theme}/"
    
    try:
        time.sleep(uniform(0.01, 0.05))
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        
        if response.status_code == 200:
            return ("found", theme)
        elif response.status_code == 403:
            readme_url = f"{url}style.css"
            readme_response = requests.head(readme_url, headers=headers, timeout=timeout)
            return ("found", theme) if readme_response.status_code == 200 else ("possible", theme)
            
    except requests.exceptions.RequestException as e:
        return ("error", f"{theme}: {str(e)}")
    
    return ("not_found", theme)

def scan_themes(url):
    global shutdown
    shutdown = False

    print(BANNER)
    
    # Parámetros del escáner
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Wordlist de temas (ruta): ", end="")
    wordlist_path = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Hilos (10): ", end="")
    threads = input().strip() or "10"
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (15s): ", end="")
    timeout = input().strip() or "15"
    
    threads = int(threads)
    timeout = int(timeout)

    try:
        with open(wordlist_path, 'r', errors='ignore') as f:
            themes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\n{Fore.RED}[!] Error: Wordlist no encontrada{Style.RESET_ALL}")
        return

    found = []
    possible = []
    errors = []

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(check_theme, url, theme, timeout) for theme in themes]
            
            with tqdm(
                total=len(themes),
                desc=f"{Fore.CYAN}⏳ Escaneando temas{Style.RESET_ALL}",
                unit="tema",
                dynamic_ncols=True,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
            ) as pbar:
                for future in as_completed(futures):
                    if shutdown:
                        break
                    result_type, data = future.result()
                    
                    if result_type == "found":
                        found.append(data)
                        pbar.write(f"{Fore.GREEN}✅ {data}{Style.RESET_ALL}")
                    elif result_type == "possible":
                        possible.append(data)
                        pbar.write(f"{Fore.YELLOW}⚠️  {data} (403){Style.RESET_ALL}")
                    elif result_type == "error":
                        errors.append(data)
                        pbar.write(f"{Fore.RED}⚠️  {data}{Style.RESET_ALL}")
                    
                    pbar.update(1)

    except KeyboardInterrupt:
        shutdown = True
        print(f"\n{Fore.RED}[!] Escaneo interrumpido{Style.RESET_ALL}")
    finally:
        print("\033[K", end="")

    # Resultados
    print(f"\n{Style.BRIGHT}{Fore.CYAN}►► {Fore.WHITE}RESULTADOS")
    print(f"{Fore.CYAN}├───────────────{Fore.WHITE}───────────────────────┤")
    print(f"{Fore.CYAN}│ {Fore.GREEN}✔ Detectados: {Fore.WHITE}{len(found):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠ Posibles:  {Fore.WHITE}{len(possible):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.RED}☠ Errores:   {Fore.WHITE}{len(errors):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}└───────────────{Fore.WHITE}───────────────────────┘\n")