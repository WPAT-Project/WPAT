import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}XML-RPC ANALYZER {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def check_xmlrpc(url):
    print(BANNER)
    xmlrpc_url = f"{url}/xmlrpc.php"
    
    try:
        # Detección inicial
        response = requests.post(xmlrpc_url, timeout=5)
        if "XML-RPC server accepts POST requests only" not in response.text:
            print(f"{Fore.RED}[ERROR] XML-RPC no detectado")
            return

        print(f"{Fore.CYAN}[INFO] XML-RPC detectado, analizando métodos...")
        
        # Métodos a verificar
        tests = {
            "system.multicall": "<?xml version='1.0'?><methodCall><methodName>system.listMethods</methodName></methodCall>",
            "pingback.ping": "<?xml version='1.0'?><methodCall><methodName>pingback.ping</methodName></methodCall>",
            "brute_force": "<?xml version='1.0'?><methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value>admin</value></param><param><value>password</value></param></params></methodCall>"
        }

        for method, payload in tests.items():
            response = requests.post(xmlrpc_url, data=payload, headers={
                'Content-Type': 'text/xml',
                'User-Agent': 'WP Audit Tool'
            })
            
            if "faultCode" not in response.text and response.status_code == 200:
                print(f"{Fore.GREEN}[VULNERABLE] Método {method} habilitado")
            else:
                print(f"{Fore.YELLOW}[SEGURO] Método {method} no disponible")

    except Exception as e:
        print(f"{Fore.RED}[ERROR] {str(e)}")