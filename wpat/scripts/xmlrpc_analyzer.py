import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}XML-RPC SECURITY AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status, prefix=""):
    status_colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN + Style.BRIGHT,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "detected": Fore.GREEN + "✔",
        "not_detected": Fore.RED + "✖"
    }
    if prefix:
        print(f"{status_colors[status]} {prefix} {Fore.WHITE}{message}")
    else:
        print(f"{status_colors[status]}[{status.upper()}] {Fore.WHITE}{message}")

def is_xmlrpc_active(target_url):
    """Mejor detección con múltiples técnicas"""
    try:
        # Método 1: Solicitud básica de listado de métodos
        payload = """<?xml version='1.0'?><methodCall><methodName>system.listMethods</methodName></methodCall>"""
        response = requests.post(target_url, data=payload, headers={'Content-Type': 'text/xml'}, timeout=10)
        
        # Detectar firmas XML-RPC
        xmlrpc_signatures = ["methodResponse", "array>", "faultCode"]
        if any(sig in response.text for sig in xmlrpc_signatures):
            return True
        
        # Método 2: Respuesta a método inexistente
        invalid_response = requests.post(
            target_url,
            data="""<?xml version='1.0'?><methodCall><methodName>fake.method</methodName></methodCall>""",
            headers={'Content-Type': 'text/xml'},
            timeout=10
        )
        
        if "faultCode" in invalid_response.text:
            return True
            
        return False
        
    except Exception:
        return False

def check_xmlrpc(url):
    print(BANNER)
    target_url = url.rstrip("/") + "/xmlrpc.php"
    print_status(f"Analizando: {target_url}", "info")
    
    try:
        # Detección principal
        xmlrpc_detected = is_xmlrpc_active(target_url)
        
        # Resultado de detección
        if xmlrpc_detected:
            print_status("XML-RPC detectado", "success", prefix="[DETECCIÓN]")
        else:
            print_status("XML-RPC no detectado", "error", prefix="[DETECCIÓN]")
            return  # Salir si no se detecta

        # Análisis de métodos
        print_status("Verificando métodos:", "info", prefix="\n[MÉTODOS]")
        methods = {
            "system.multicall": "Ejecución múltiple de métodos",
            "pingback.ping": "Posible vector DDoS",
            "wp.getUsersBlogs": "Fuerza bruta de credenciales",
            "demo.sayHello": "Método de prueba"
        }
        
        for method, desc in methods.items():
            payload = f"""<?xml version='1.0'?><methodCall><methodName>{method}</methodName></methodCall>"""
            response = requests.post(target_url, data=payload, headers={'Content-Type': 'text/xml'}, timeout=10)
            
            if "faultCode" not in response.text and response.status_code == 200:
                print_status(f"{method}: {desc}", "warning", prefix="•")
            else:
                print_status(f"{method}: Inaccesible", "success", prefix="•")
                
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")