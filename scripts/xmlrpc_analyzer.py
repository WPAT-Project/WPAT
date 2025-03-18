import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}XML-RPC SECURITY AUDITOR {Fore.CYAN}■
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

def check_xmlrpc(url):
    print(BANNER)
    target_url = url.rstrip("/") + "/xmlrpc.php"
    print_status(f"Analizando XML-RPC en: {target_url}", "info")
    
    try:
        # Detección básica
        response = requests.post(target_url, timeout=10)
        if "XML-RPC server accepts POST requests only" not in response.text:
            print_status("XML-RPC no detectado", "error")
            return
        
        # Verificar métodos peligrosos
        methods = {
            "system.multicall": "Permite ejecución múltiple de métodos",
            "pingback.ping": "Posibles ataques DDoS",
            "wp.getUsersBlogs": "Fuerza bruta de credenciales"
        }
        
        for method, desc in methods.items():
            payload = f"""<?xml version='1.0'?>
            <methodCall>
                <methodName>{method}</methodName>
                <params>
                    <param><value>1</value></param>
                </params>
            </methodCall>"""
            
            response = requests.post(
                target_url,
                data=payload,
                headers={'Content-Type': 'text/xml'},
                timeout=10
            )
            
            if "faultCode" not in response.text and response.status_code == 200:
                print_status(f"Método {method} habilitado: {desc}", "warning")
            else:
                print_status(f"Método {method} desactivado", "success")
                
    except Exception as e:
        print_status(f"Error en XML-RPC: {str(e)}", "error")