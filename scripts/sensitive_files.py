import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}SENSITIVE FILES SCANNER {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def scan_sensitive_files(url):
    print(BANNER)
    files = [
        "wp-config.php", "wp-config.php.bak", "wp-config.php.save",
        ".htaccess", "debug.log", "error_log", "wp-admin/install.php",
        "phpinfo.php", "license.txt", "readme.html"
    ]
    
    print(f"{Fore.CYAN}[INFO] Escaneando {len(files)} archivos sensibles...")
    
    for file in files:
        try:
            response = requests.get(f"{url}/{file}", timeout=5, headers={'User-Agent': 'WP Audit Tool'})
            if response.status_code == 200 and len(response.text) > 0:
                print(f"{Fore.GREEN}[EXPUESTO] {file}")
            else:
                print(f"{Fore.YELLOW}[PROTEGIDO] {file}")
        except:
            print(f"{Fore.RED}[ERROR] No se pudo verificar {file}")