import requests
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE} SECURITY.TXT INSPECTOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status, prefix="", icon=""):
    status_colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "detected": "#00FFAA"
    }
    icons = {
        "info": "🌐",
        "success": "✅",
        "error": "❌",
        "detected": "📄",
        "scan": "🔎"
    }
    color = status_colors.get(status, Fore.WHITE)
    formatted_prefix = f"{Style.BRIGHT}{color}{icons.get(icon, '')} {prefix}"
    print(f"{formatted_prefix}{Style.RESET_ALL} {Fore.WHITE}{message}")

def check_security_txt(url):
    print(BANNER)
    
    # Normalización de URL
    original_url = url
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = f"https://{url}"
        print_status(f"{Fore.YELLOW}'{original_url}' {Fore.WHITE}→ {Fore.CYAN}{url}", 
                    "info", prefix="[CONFIG]", icon="scan")

    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        print_status("Formato de URL inválido", "error", prefix="[ERROR]", icon="error")
        return

    target_url = f"{parsed_url.scheme}://{parsed_url.netloc}/.well-known/security.txt"
    print_status(f"{Fore.WHITE}Objetivo escaneado:{Style.RESET_ALL}\n{'-'*45}", "info", prefix="🎯 [TARGET]")
    print(f"{Fore.CYAN}{target_url}\n{'-'*45}")
    
    try:
        response = requests.get(target_url, timeout=10, headers={'User-Agent': 'SecurityTxtInspector/3.0'})
        response.raise_for_status()
        
        # Resultado exitoso
        content = response.text.replace('\n', '\n    ')
        print_status("", "success", prefix=f"{Fore.GREEN}⮞⮞⮞ DETECTADO", icon="success")
        print(f"""
{Fore.CYAN}╭───────────────── METADATOS ─────────────────╮
{Fore.WHITE}│ {Fore.CYAN}• URL: {target_url}
{Fore.WHITE}│ {Fore.CYAN}• Estado: {Fore.GREEN}{response.status_code} OK
{Fore.WHITE}│ {Fore.CYAN}• Tamaño: {Fore.YELLOW}{len(response.text)} caracteres
{Fore.CYAN}╰─────────────────────────────────────────────╯

{Fore.CYAN}╭────────────── CONTENIDO (preview) ────────────╮
{Fore.WHITE}    {content[:300]}{'...' if len(response.text) > 300 else ''}
{Fore.CYAN}╰─────────────────────────────────────────────╯
        """)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print_status("Archivo no encontrado en la ruta estándar", 
                        "error", prefix=f"{Fore.RED}⮞⮞⮞ NO DETECTADO", icon="error")
        else:
            print_status(f"Error del servidor: {Fore.RED}HTTP {response.status_code}", 
                        "error", prefix="[ERROR]", icon="error")
    
    except requests.exceptions.RequestException as err:
        print_status(f"Fallo de conexión: {Fore.RED}{err}", "error", prefix="[ERROR]", icon="error")
    
    except Exception as e:
        print_status(f"Error crítico: {Fore.RED}{str(e)}", "error", prefix="[ERROR]", icon="error")
