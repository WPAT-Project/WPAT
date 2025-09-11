import requests
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}USER ENUMERATION DETECTOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status):
    status_colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN + Style.BRIGHT,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    print(f"{status_colors[status]}[{status.upper()}] {Fore.WHITE}{message}")

def normalize_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    return url.rstrip("/") + "/"

def check_author_archives(url, max_id=100, timeout=5, max_workers=20):
    detected_users = {}
    print_status(f"Probando Author Archives (/?author=1-{max_id})", "info")
    
    def check_user_id(user_id):
        try:
            response = requests.get(
                f"{url}?author={user_id}",
                allow_redirects=True,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36'}
            )
            
            if response.history and "author" in response.url:
                username = response.url.split("/author/")[-1].strip("/")
                return (user_id, username)
        except Exception:
            return None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_user_id, user_id) for user_id in range(1, max_id + 1)]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                user_id, username = result
                detected_users[user_id] = username
                print_status(f"Usuario ID {user_id}: {Fore.YELLOW}{username}", "success")
    
    return detected_users

def check_rest_api(url, timeout=5):
    detected_users = []
    print_status("Probando REST API (/wp-json/wp/v2/users)", "info")
    
    try:
        api_url = f"{url}wp-json/wp/v2/users"
        response = requests.get(
            api_url,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36'}
        )
        
        if response.status_code == 200:
            try:
                users = response.json()
                detected_users.extend([user["slug"] for user in users])
                for user in users:
                    print_status(f"Usuario detectado via REST API: {Fore.YELLOW}{user['slug']}", "success")
            except ValueError:
                print_status("Respuesta JSON inválida", "error")
                
    except Exception as e:
        print_status(f"Error en REST API: {str(e)}", "error")
    
    return detected_users

def check_oembed(url, timeout=5):
    detected_users = []
    print_status("Probando oEmbed (/wp-json/oembed/1.0/embed)", "info")
    
    try:
        oembed_url = f"{url}wp-json/oembed/1.0/embed?url={url}"
        response = requests.get(
            oembed_url,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if author_name := data.get("author_name"):
                detected_users.append(author_name)
                print_status(f"Usuario detectado via oEmbed: {Fore.YELLOW}{author_name}", "success")
                
    except Exception as e:
        print_status(f"Error en oEmbed: {str(e)}", "error")
    
    return detected_users

def check_xmlrpc(url, timeout=5):
    detected_users = []
    print_status("Probando XML-RPC (/xmlrpc.php)", "info")
    
    try:
        xmlrpc_url = f"{url}xmlrpc.php"
        
        # Primero verificamos si XML-RPC está activo
        response = requests.post(
            xmlrpc_url,
            data="""<?xml version="1.0"?>
            <methodCall>
                <methodName>system.listMethods</methodName>
                <params></params>
            </methodCall>""",
            timeout=timeout,
            headers={'Content-Type': 'application/xml'}
        )
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                methods = [method.text for method in root.findall('.//string')]
                
                if 'wp.getUsers' in methods:
                    print_status("XML-RPC habilitado y wp.getUsers disponible", "success")
                    
                    # Intentamos obtener usuarios
                    users_payload = """<?xml version="1.0"?>
                    <methodCall>
                        <methodName>wp.getUsers</methodName>
                        <params>
                            <param><value>1</value></param>
                            <param><value>admin</value></param>
                            <param><value>password</value></param>
                        </params>
                    </methodCall>"""
                    
                    users_response = requests.post(
                        xmlrpc_url,
                        data=users_payload,
                        timeout=timeout,
                        headers={'Content-Type': 'application/xml'}
                    )
                    
                    if users_response.status_code == 200:
                        try:
                            users_root = ET.fromstring(users_response.text)
                            for member in users_root.findall('.//member'):
                                name = member.find('name')
                                value = member.find('value/string')
                                if name is not None and value is not None and name.text == 'username':
                                    username = value.text
                                    detected_users.append(username)
                                    print_status(f"Usuario detectado via XML-RPC: {Fore.YELLOW}{username}", "success")
                        except ET.ParseError:
                            print_status("Error al parsear respuesta de usuarios XML-RPC", "error")
                else:
                    print_status("XML-RPC habilitado pero wp.getUsers no disponible", "warning")
            except ET.ParseError:
                print_status("Error al parsear respuesta de métodos XML-RPC", "error")
        else:
            print_status("XML-RPC no disponible", "info")
                
    except Exception as e:
        print_status(f"Error en XML-RPC: {str(e)}", "error")
    
    return detected_users

def check_user_enumeration(url):
    print(BANNER)
    target_url = normalize_url(url)
    print_status(f"Iniciando análisis en: {target_url}", "info")
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}ID máximo para Author Archives (10): ", end="")
    max_author_id = input().strip()
    max_author_id = int(max_author_id) if max_author_id else 10
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout en segundos (5): ", end="")
    timeout = input().strip()
    timeout = int(timeout) if timeout else 5
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Número de hilos (20): ", end="")
    max_workers = input().strip()
    max_workers = int(max_workers) if max_workers else 20
    
    # Ejecutar todos los checks
    author_users = check_author_archives(target_url, max_author_id, timeout, max_workers)
    rest_api_users = check_rest_api(target_url, timeout)
    oembed_users = check_oembed(target_url, timeout)
    xmlrpc_users = check_xmlrpc(target_url, timeout)
    
    # Resumen final (estilo original mejorado)
    print(f"\n{Style.BRIGHT}{Fore.CYAN}■ Resumen de enumeración ■")
    
    summary = []
    if author_users:
        summary.append(f"{Fore.GREEN}• Author Archives: {Fore.YELLOW}{', '.join(author_users.values())}")
    if rest_api_users:
        summary.append(f"{Fore.GREEN}• REST API: {Fore.YELLOW}{', '.join(rest_api_users)}")
    if oembed_users:
        summary.append(f"{Fore.GREEN}• oEmbed: {Fore.YELLOW}{', '.join(oembed_users)}")
    if xmlrpc_users:
        summary.append(f"{Fore.GREEN}• XML-RPC: {Fore.YELLOW}{', '.join(xmlrpc_users)}")
        
    if not summary:
        print_status("No se detectaron usuarios expuestos", "info")
    else:
        print("\n".join(summary))

def check_user_enumeration_gui(url):
    print(BANNER)
    target_url = normalize_url(url)
    print_status(f"Iniciando análisis en: {target_url}", "info")
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}ID máximo para Author Archives (10): ", end="")
    max_author_id = 10
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout en segundos (5): ", end="")
    timeout = 5
    
    print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Número de hilos (20): ", end="")
    max_workers = 20
    
    # Ejecutar todos los checks
    author_users = check_author_archives(target_url, max_author_id, timeout, max_workers)
    rest_api_users = check_rest_api(target_url, timeout)
    oembed_users = check_oembed(target_url, timeout)
    xmlrpc_users = check_xmlrpc(target_url, timeout)
    
    # Resumen final (estilo original mejorado)
    print(f"\n{Style.BRIGHT}{Fore.CYAN}■ Resumen de enumeración ■")
    
    summary = []
    if author_users:
        summary.append(f"{Fore.GREEN}• Author Archives: {Fore.YELLOW}{', '.join(author_users.values())}")
    if rest_api_users:
        summary.append(f"{Fore.GREEN}• REST API: {Fore.YELLOW}{', '.join(rest_api_users)}")
    if oembed_users:
        summary.append(f"{Fore.GREEN}• oEmbed: {Fore.YELLOW}{', '.join(oembed_users)}")
    if xmlrpc_users:
        summary.append(f"{Fore.GREEN}• XML-RPC: {Fore.YELLOW}{', '.join(xmlrpc_users)}")
        
    if not summary:
        print_status("No se detectaron usuarios expuestos", "info")
    else:
        print("\n".join(summary))