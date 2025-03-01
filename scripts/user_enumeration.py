import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}USER ENUMERATION DETECTOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status):
    status_colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN + Style.BRIGHT,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    print(f"{status_colors[status]}[{status.upper()}] {Fore.WHITE}{message}")

def check_user_enumeration(url):
    print(BANNER)
    print_status(f"Iniciando análisis en: {url}", "info")
    
    endpoints = {
        "REST API Users": "/wp-json/wp/v2/users",
        "Author Param": "/?author=1",
        "oEmbed Data": "/wp-json/oembed/1.0/embed"
    }

    for name, endpoint in endpoints.items():
        try:
            full_url = f"{url}{endpoint}"
            response = requests.get(full_url, timeout=10, headers={'User-Agent': 'WP Audit Tool'})
            
            if response.status_code == 200:
                if "users" in endpoint or "author" in endpoint:
                    users = response.json() if "users" in endpoint else [{"id": 1}]
                    print_status(f"{name} expuesto", "success")
                    print(f"{Fore.WHITE}• Usuarios detectados: {len(users)}")
                else:
                    print_status(f"{name} accesible", "warning")
            else:
                print_status(f"{name} seguro", "info")
                
        except Exception as e:
            print_status(f"Error en {name}: {str(e)}", "error")