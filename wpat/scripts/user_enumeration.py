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

def normalize_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    return url.rstrip("/") + "/"

def check_author_archives(url):
    detected_users = {}
    print_status("Probando Author Archives (/?author=1-10)", "info")
    
    for user_id in range(1, 11):
        try:
            response = requests.get(
                f"{url}?author={user_id}",
                allow_redirects=True,
                timeout=10,
                headers={'User-Agent': 'WP Audit Tool'}
            )
            
            if response.history and "author" in response.url:
                username = response.url.split("/author/")[-1].strip("/")
                detected_users[user_id] = username
                print_status(f"Usuario ID {user_id}: {Fore.YELLOW}{username}", "success")
                
        except Exception as e:
            print_status(f"Error en ID {user_id}: {str(e)}", "error")
    
    return detected_users

def check_rest_api(url):
    detected_users = []
    print_status("Probando REST API (/wp-json/wp/v2/users)", "info")
    
    page = 1
    while True:
        try:
            api_url = f"{url}wp-json/wp/v2/users?page={page}"
            response = requests.get(
                api_url,
                timeout=10,
                headers={'User-Agent': 'WP Audit Tool'}
            )
            
            if response.status_code != 200:
                break
                
            try:
                users = response.json()
                detected_users.extend([user["slug"] for user in users])
                
                if len(users) < 10:
                    break
                page += 1
                    
            except ValueError:
                print_status("Respuesta JSON inválida", "error")
                break
                
        except Exception as e:
            print_status(f"Error en REST API: {str(e)}", "error")
            break
    
    return detected_users

def check_oembed(url):
    detected_users = []
    print_status("Probando oEmbed (/wp-json/oembed/1.0/embed)", "info")
    
    try:
        oembed_url = f"{url}wp-json/oembed/1.0/embed?url={url}"
        response = requests.get(
            oembed_url,
            timeout=10,
            headers={'User-Agent': 'WP Audit Tool'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if author_name := data.get("author_name"):
                detected_users.append(author_name)
                print_status(f"Usuario detectado via oEmbed: {Fore.YELLOW}{author_name}", "success")
                
    except Exception as e:
        print_status(f"Error en oEmbed: {str(e)}", "error")
    
    return detected_users

def check_xmlrpc(url):
    print_status("Probando XML-RPC (/xmlrpc.php)", "info")
    
    try:
        xmlrpc_url = f"{url}xmlrpc.php"
        payload = """<?xml version="1.0"?>
        <methodCall>
            <methodName>wp.getUsers</methodName>
            <params>
                <param><value>1</value></param>
                <param><value>admin</value></param>
                <param><value>password</value></param>
            </params>
        </methodCall>"""
        
        response = requests.post(
            xmlrpc_url,
            data=payload,
            timeout=10,
            headers={'Content-Type': 'application/xml'}
        )
        
        if response.status_code == 200:
            if "Incorrect username or password" in response.text:
                print_status("XML-RPC habilitado (posible enumeración)", "warning")
            else:
                print_status("XML-RPC no permite enumeración", "info")
                
    except Exception as e:
        print_status(f"Error en XML-RPC: {str(e)}", "error")

def check_user_enumeration(url):
    print(BANNER)
    target_url = normalize_url(url)
    print_status(f"Iniciando análisis en: {target_url}", "info")
    
    # Ejecutar todos los checks
    author_users = check_author_archives(target_url)
    rest_api_users = check_rest_api(target_url)
    oembed_users = check_oembed(target_url)
    check_xmlrpc(target_url)  # Solo muestra estado, no retorna usuarios
    
    # Resumen final (estilo original mejorado)
    print(f"\n{Style.BRIGHT}{Fore.CYAN}■ Resumen de enumeración ■")
    
    summary = []
    if author_users:
        summary.append(f"{Fore.GREEN}• Author Archives: {Fore.YELLOW}{', '.join(author_users.values())}")
    if rest_api_users:
        summary.append(f"{Fore.GREEN}• REST API: {Fore.YELLOW}{', '.join(rest_api_users)}")
    if oembed_users:
        summary.append(f"{Fore.GREEN}• oEmbed: {Fore.YELLOW}{', '.join(oembed_users)}")
        
    if not summary:
        print_status("No se detectaron usuarios expuestos", "info")
    else:
        print("\n".join(summary))