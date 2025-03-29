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
■ {Fore.WHITE}WORDPRESS PLUGIN SCANNER {Fore.CYAN}■
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

def cargar_wordlist(ruta):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(ruta, 'r', encoding=encoding, errors='strict') as f:
                contenido = f.read()
                print(f"{Fore.GREEN}✅ Encoding detectado: {encoding}{Style.RESET_ALL}")
                return [linea.strip() for linea in contenido.splitlines() if linea.strip()], len(contenido.splitlines())
        except UnicodeDecodeError:
            continue
    
    try:
        with open(ruta, 'r', encoding='latin-1', errors='replace') as f:
            lineas = f.readlines()
            print(f"{Fore.YELLOW}⚠️  Usando encoding latín-1 con reemplazo{Style.RESET_ALL}")
            return [linea.strip() for linea in lineas if linea.strip()], len(lineas)
    except Exception as e:
        raise ValueError(f"Error de carga: {str(e)}")

def check_plugin(target_url, plugin, timeout=15):
    global shutdown
    if shutdown:
        return ("cancelled", None)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    url = f"{target_url.rstrip('/')}/wp-content/plugins/{plugin}/"
    
    try:
        time.sleep(uniform(0.01, 0.05))
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        
        if response.status_code == 200:
            return ("found", plugin)
        elif response.status_code == 403:
            readme_url = f"{url}readme.txt"
            readme_response = requests.head(readme_url, headers=headers, timeout=timeout)
            return ("found", plugin) if readme_response.status_code == 200 else ("possible", plugin)
            
    except requests.exceptions.RequestException as e:
        return ("error", f"{plugin}: {str(e)}")
    
    return ("not_found", plugin)

def scan_plugins(url):
    global shutdown
    shutdown = False

    print(BANNER)
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Wordlist (ruta): ", end="")
    wordlist_path = input().strip()
    
    try:
        start_time = time.time()
        plugins, total_lineas = cargar_wordlist(wordlist_path)
        tiempo_carga = time.time() - start_time
        print(f"{Fore.CYAN}[i] {total_lineas} plugins cargados en {tiempo_carga:.2f}s{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        return
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Hilos (10): ", end="")
    threads = input().strip() or "10"
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (15s): ", end="")
    timeout = input().strip() or "15"
    
    threads = int(threads)
    timeout = int(timeout)

    found = []
    possible = []
    errors = []

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(check_plugin, url, plugin, timeout) for plugin in plugins]
            
            with tqdm(
                total=len(plugins),
                desc=f"{Fore.CYAN}⏳ Progreso{Style.RESET_ALL}",
                unit="plugin",
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

    print(f"\n{Style.BRIGHT}{Fore.CYAN}►► {Fore.WHITE}RESULTADOS")
    print(f"{Fore.CYAN}├───────────────{Fore.WHITE}───────────────────────┤")
    print(f"{Fore.CYAN}│ {Fore.GREEN}✔ Confirmados: {Fore.WHITE}{len(found):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.YELLOW}⚠ Posibles:   {Fore.WHITE}{len(possible):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}│ {Fore.RED}☠ Errores:    {Fore.WHITE}{len(errors):<18} {Fore.CYAN}│")
    print(f"{Fore.CYAN}└───────────────{Fore.WHITE}───────────────────────┘\n")
