import requests
from colorama import Fore, Style, init
import xml.etree.ElementTree as ET

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
    try:
        payload = """<?xml version='1.0'?><methodCall><methodName>system.listMethods</methodName></methodCall>"""
        response = requests.post(target_url, data=payload, headers={'Content-Type': 'text/xml'}, timeout=10)
        
        xmlrpc_signatures = ["methodResponse", "array>", "faultCode"]
        if any(sig in response.text for sig in xmlrpc_signatures):
            return True
            
        invalid_response = requests.post(
            target_url,
            data="""<?xml version='1.0'?><methodCall><methodName>fake.method</methodName></methodCall>""",
            headers={'Content-Type': 'text/xml'},
            timeout=10
        )
        
        return "faultCode" in invalid_response.text
        
    except Exception:
        return False

def check_xmlrpc(url):
    print(BANNER)
    target_url = url.rstrip("/") + "/xmlrpc.php"
    print_status(f"Analizando: {target_url}", "info")
    
    try:
        xmlrpc_detected = is_xmlrpc_active(target_url)
        
        if xmlrpc_detected:
            print_status("XML-RPC detectado", "success", prefix="[DETECCIÓN]")
            
            # Listar todos los métodos
            print_status("Listando métodos disponibles:", "info", prefix="\n[MÉTODOS XML-RPC]")
            list_methods_payload = """<?xml version='1.0' encoding='utf-8'?>
            <methodCall>
                <methodName>system.listMethods</methodName>
                <params></params>
            </methodCall>"""
            
            response = requests.post(
                target_url, 
                data=list_methods_payload,
                headers={'Content-Type': 'text/xml'},
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    root = ET.fromstring(response.text)
                    methods = []
                    namespace = {'ex': 'http://ws.apache.org/xmlrpc/namespaces/extensions'}
                    
                    for value in root.findall(".//ex:array/ex:data/ex:value/ex:string", namespace):
                        methods.append(value.text.strip())
                    
                    if not methods:
                        for value in root.findall(".//array/data/value/string"):
                            methods.append(value.text.strip())
                    
                    if methods:
                        for method in sorted(methods):
                            print_status(f"{method}", "detected", prefix="•")
                    else:
                        print_status("No se encontraron métodos", "warning")
                        
                except ET.ParseError:
                    print_status("Error parseando la respuesta XML", "error")
                    
            else:
                print_status(f"Error HTTP {response.status_code}", "error")

            # Análisis de métodos específicos
            print_status("Analizando métodos críticos:", "info", prefix="\n[ANÁLISIS]")
            critical_methods = {
                "system.multicall": "Permite ejecución múltiple de métodos",
                "pingback.ping": "Posible vector DDoS",
                "wp.getUsersBlogs": "Puede usarse para fuerza bruta",
                "metaWeblog.newPost": "Creación de posts remota"
            }
            
            for method, desc in critical_methods.items():
                if method in methods:
                    # Probar si el método está realmente accesible
                    test_payload = f"""<?xml version='1.0' encoding='utf-8'?>
                    <methodCall>
                        <methodName>{method}</methodName>
                        <params></params>
                    </methodCall>"""
                    
                    try:
                        test_response = requests.post(
                            target_url,
                            data=test_payload,
                            headers={'Content-Type': 'text/xml'},
                            timeout=10
                        )
                        
                        if test_response.status_code == 200 and "faultCode" not in test_response.text:
                            print_status(f"{method}: {desc}", "warning", prefix=f"{Fore.RED}⚠️ ACCESIBLE")
                        else:
                            print_status(f"{method}: {desc}", "success", prefix=f"{Fore.YELLOW}🔒 RESTRINGIDO")
                    except Exception:
                        print_status(f"{method}: {desc}", "success", prefix=f"{Fore.YELLOW}🔒 RESTRINGIDO")
                else:
                    print_status(f"{method}: No disponible", "success", prefix=f"{Fore.GREEN}✓")
            
        else:
            print_status("XML-RPC no detectado", "error", prefix="[DETECCIÓN]")
            
    except Exception as e:
        print_status(f"Error: {str(e)}", "error")
