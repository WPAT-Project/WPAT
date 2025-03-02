import requests
import time
import sys
from random import uniform
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style

BANNER = f"""{Fore.CYAN}{Style.BRIGHT}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}ESCÁNER DE PLUGINS WORDPRESS {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

def print_progress(current, total, start_line):
    sys.stdout.write(
        f"\033[s\033[{start_line};1H\033[K"
        f"{Fore.CYAN}[*]{Style.RESET_ALL} Progreso: {current}/{total} plugins\n"
        "\033[u"
    )
    sys.stdout.flush()

def check_plugin(target_url, plugin, timeout=10):
    headers = {'User-Agent': 'WP Audit Tool'}
    url = f"{target_url.rstrip('/')}/wp-content/plugins/{plugin}/"
    
    try:
        time.sleep(uniform(0.01, 0.1))
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        
        if response.status_code == 200:
            return ("found", plugin, url)
        elif response.status_code == 403:
            return ("possible", plugin, url)
        return (None, None, None)
        
    except Exception as e:
        return ("error", plugin, str(e))

def scan_plugins(url, is_full_audit=False, wordlist=None, threads=10):
    if not is_full_audit:
        print(BANNER)
        base_line = BANNER.count('\n') + 4
    else:
        base_line = 3  # Posición base en auditoría completa

    try:
        if not wordlist:
            wordlist = input(f"\n{Fore.CYAN}↳ Ruta de la wordlist {Fore.YELLOW}(ej: plugins.txt){Fore.WHITE}: ").strip()
        
        threads = max(1, min(50, int(threads)))
        
        with open(wordlist, 'r', errors='ignore') as f:
            plugins = [line.strip() for line in f if line.strip()]
            
    except Exception as e:
        print(f"\n{Fore.RED}[✗] Error: {e}{Style.RESET_ALL}")
        return

    found = []
    possible = []
    errors = []
    total = len(plugins)
    result_count = 0
    
    start_line = base_line + 1  # Línea de inicio del progreso
    print_progress(0, total, start_line)

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_plugin, url, plugin): plugin for plugin in plugins}
            processed = 0

            audit_interrupted = False
            
            for future in as_completed(futures):
                if audit_interrupted: break
                
                result = future.result()
                processed = min(processed + 1, total)
                
                if result and result[0]:
                    result_type, plugin, extra = result
                    
                    if result_type == "found": found.append(plugin)
                    elif result_type == "possible": possible.append(plugin)
                    elif result_type == "error": errors.append(plugin)
                    
                    # Mostrar resultado en posición dinámica
                    result_line = start_line + 2 + result_count
                    sys.stdout.write(f"\033[s\033[{result_line};0H\033[K")
                    color = Fore.GREEN if result_type == "found" else Fore.YELLOW if result_type == "possible" else Fore.RED
                    symbol = "✓" if result_type == "found" else "!" if result_type == "possible" else "✗"
                    print(f"{color}[{symbol}] {plugin.ljust(25)}{Fore.WHITE}→ {extra if result_type != 'error' else 'Error de conexión'}\n")
                    sys.stdout.write("\033[u")
                    result_count += 1
                
                print_progress(processed, total, start_line)
                
    except KeyboardInterrupt:
        sys.stdout.write("\033[0;0H\033[J")
        print(f"\n{Fore.RED}[✗] Escaneo interrumpido!{Style.RESET_ALL}")
        return

    # Resultados finales posicionados correctamente
    sys.stdout.write(f"\033[{start_line + result_count + 2};0H")
    print(f"{Fore.CYAN}[*] Resultados:")
    print(f"{Fore.GREEN}• Plugins detectados: {len(found)}")
    print(f"{Fore.YELLOW}• Posibles falsos negativos: {len(possible)}")
    print(f"{Fore.RED}• Errores de conexión: {len(errors)}")