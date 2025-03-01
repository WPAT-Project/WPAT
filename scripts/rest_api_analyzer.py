import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}REST API AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def check_rest_api(url):
    print(BANNER)
    endpoints = [
        "/wp-json/wp/v2/users",
        "/wp-json/wp/v2/posts?per_page=1",
        "/wp-json/wp/v2/comments",
        "/wp-json/wp/v2/settings",
        "/wp-json/wp/v2/taxonomies"
    ]
    
    print(f"{Fore.CYAN}[INFO] Probando {len(endpoints)} endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{url}{endpoint}", timeout=5, headers={'User-Agent': 'WP Audit Tool'})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"{Fore.GREEN}[ABIERTO] {endpoint} ({len(data)} resultados)")
                else:
                    print(f"{Fore.YELLOW}[ACCESIBLE] {endpoint} (sin datos)")
            else:
                print(f"{Fore.RED}[PROTEGIDO] {endpoint}")
        except:
            print(f"{Fore.RED}[ERROR] No se pudo verificar {endpoint}")