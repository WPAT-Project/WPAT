import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
╔══════════════════════════════╗
║ {Fore.WHITE}AUDITORÍA DETALLADA DE REST API {Fore.CYAN}║
╚══════════════════════════════╝
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
    
    print(f"{Style.BRIGHT}{Fore.CYAN}■ {Fore.WHITE}Probando {len(endpoints)} endpoints...\n")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{url}{endpoint}", timeout=5, headers={'User-Agent': 'WP Audit Tool'})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"{Fore.GREEN}{Style.BRIGHT}[ABIERTO] {Fore.WHITE}{endpoint} ({len(data)} resultados)")
                else:
                    print(f"{Fore.YELLOW}{Style.BRIGHT}[ACCESIBLE] {Fore.WHITE}{endpoint}")
            else:
                print(f"{Fore.RED}{Style.BRIGHT}[PROTEGIDO] {Fore.WHITE}{endpoint}")
        except:
            print(f"{Fore.RED}{Style.BRIGHT}[ERROR] {Fore.WHITE}No se pudo verificar {endpoint}")