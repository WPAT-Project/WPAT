#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlparse
import urllib3
from colorama import init, Fore, Style
import sys
from collections import defaultdict

# Inicializar colorama
init(autoreset=True)

# Desactivar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}CORS SECURITY AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
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

def print_header(text):
    print(f"\n{Style.BRIGHT}{Fore.CYAN}■ {text} ■{Style.RESET_ALL}")

def print_method_result(method, status_code, acao, acac, content_type=None, origin_tested=None):
    """Imprime los resultados de una prueba de método"""
    print(f"\n{Style.BRIGHT}{Fore.YELLOW}▶ {method} (Origen: {origin_tested})")
    print(f"{Style.DIM}{'─'*50}")
    
    status_color = Fore.GREEN if status_code == 200 else Fore.YELLOW if str(status_code).startswith('2') or str(status_code).startswith('3') else Fore.RED
    acao_color = Fore.RED if acao and ('evil.com' in acao or acao == '*' or acao == 'null') else Fore.WHITE
    acac_color = Fore.RED if acac == 'true' else Fore.WHITE
    
    print(f"{Style.BRIGHT}Estado: {status_color}{status_code}")
    print(f"{Style.BRIGHT}ACAO: {acao_color}{acao}")
    print(f"{Style.BRIGHT}ACAC: {acac_color}{acac}")
    
    if content_type:
        print(f"{Style.BRIGHT}Tipo de Contenido: {Fore.WHITE}{content_type}")

def check_dangerous_configs(headers, origin):
    """Verifica configuraciones CORS peligrosas"""
    vulnerabilities = []
    
    acao = headers.get('Access-Control-Allow-Origin', '')
    acac = headers.get('Access-Control-Allow-Credentials', '')
    acah = headers.get('Access-Control-Allow-Headers', '')
    acam = headers.get('Access-Control-Allow-Methods', '')
    
    # Verificar origen reflejado sin validación
    if acao == origin:
        vulnerabilities.append("Origen reflejado sin validación")
    
    # Verificar wildcard con credenciales
    if acao == '*' and acac == 'true':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Origin: * con Access-Control-Allow-Credentials: true")
    
    # Verificar headers permitidos con wildcard
    if acah == '*':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Headers: *")
    
    # Verificar origen null
    if acao == 'null':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Origin: null")
    
    # Verificar métodos peligrosos permitidos
    if acam and any(method in acam for method in ['PUT', 'DELETE', 'POST']):
        vulnerabilities.append(f"Métodos potencialmente peligrosos permitidos: {acam}")
    
    # Verificar si expone headers sensibles
    exposed_headers = headers.get('Access-Control-Expose-Headers', '')
    sensitive_headers = ['authorization', 'cookie', 'set-cookie', 'token', 'auth']
    if any(header in exposed_headers.lower() for header in sensitive_headers):
        vulnerabilities.append(f"Headers sensibles expuestos: {exposed_headers}")
    
    return vulnerabilities

def check_subdomain_vulnerability(url, verify_ssl=False, timeout=10):
    """Verifica vulnerabilidades de subdominios wildcard"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Extraer el dominio base (ej: example.com de api.example.com)
        if domain.count('.') >= 2:
            base_domain = '.'.join(domain.split('.')[-2:])
            
            # Probar con subdominio aleatorio
            random_subdomain = f"random123.{base_domain}"
            test_origin = f"{parsed.scheme}://{random_subdomain}"
            
            session = requests.Session()
            session.verify = verify_ssl
            if not verify_ssl:
                session.trust_env = False
            
            headers = {
                'Origin': test_origin,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(url, headers=headers, timeout=timeout)
            acao = response.headers.get('Access-Control-Allow-Origin', '')
            
            if acao == test_origin or acao == '*':
                return True, test_origin
                
        return False, None
        
    except Exception:
        return False, None

def validate_url(url, verify_ssl=False, timeout=10):
    """Valida la URL antes de escanear"""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            print_status("URL inválida. Asegúrate de incluir el protocolo (http:// o https://)", "error")
            return False

        print_status("Verificando URL...", "info")
        
        session = requests.Session()
        session.verify = verify_ssl
        if not verify_ssl:
            session.trust_env = False
        
        response = session.get(url, timeout=timeout)
        
        if response.status_code >= 400:
            print_status(f"La URL devuelve código de estado {response.status_code}", "warning")
            # No retornamos False aún, podría ser que requiera autenticación
        
        # Probar con varios orígenes en lugar de solo uno
        test_origins = [
            'https://evil.com',
            'http://evil.com',
            'null',
            'https://attacker.com',
            'https://example.com'
        ]
        
        cors_detected = False
        for origin in test_origins:
            try:
                headers = {'Origin': origin}
                options_response = session.options(url, headers=headers, timeout=timeout)
                
                cors_headers = {
                    'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Methods',
                    'Access-Control-Allow-Headers',
                    'Access-Control-Allow-Credentials',
                    'Access-Control-Max-Age'
                }
                
                if any(header in options_response.headers for header in cors_headers):
                    cors_detected = True
                    break
                    
            except:
                continue
                
        if cors_detected:
            print_status("URL válida para análisis CORS", "success")
            return True
        else:
            print_status("La URL no tiene configuraciones CORS visibles", "warning")
            # Preguntar si desea continuar de todos modos
            print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}¿Continuar con el escaneo? [s/N]: ", end="")
            choice = input().strip().lower()
            return choice == 's' or choice == 'y'
            
    except requests.exceptions.RequestException as e:
        print_status(f"Error de conexión: {str(e)}", "error")
        return False
    except Exception as e:
        print_status(f"Error inesperado: {str(e)}", "error")
        return False

def test_json_hijacking(url, session, headers, timeout):
    """Prueba para ver si es posible robar datos JSON"""
    try:
        # Intentar obtener una respuesta JSON
        json_headers = headers.copy()
        json_headers['Accept'] = 'application/json'
        
        response = session.get(url, headers=json_headers, timeout=timeout)
        
        if 'application/json' in response.headers.get('Content-Type', '').lower():
            acao = response.headers.get('Access-Control-Allow-Origin', '')
            acac = response.headers.get('Access-Control-Allow-Credentials', '')
            
            # Si hay CORS configurado para JSON, podría ser vulnerable
            if acao and (acao == '*' or ('evil.com' in acao and acac == 'true')):
                return True, response.json() if response.content else "Respuesta vacía"
                
    except Exception:
        pass
        
    return False, None

def parse_headers(headers_str):
    """Parsea los headers personalizados"""
    headers = {}
    for header in headers_str:
        try:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
        except ValueError:
            print_status(f"Header inválido: {header}", "warning")
    return headers

def print_method_table_row(row, first_row=False):
    """Imprime una sola fila de la tabla de resultados."""
    if first_row:
        # Imprimir encabezado si es la primera fila
        print()
        print(f"{Style.BRIGHT}{Fore.CYAN}{'─'*100}")
        print(f"{Style.BRIGHT}{Fore.CYAN}  RESUMEN POR (ORIGEN + MÉTODO)")
        print(f"{Style.BRIGHT}{Fore.CYAN}{'─'*100}")
        header = f"{'Origin':<30} {'Method':<7} {'Status':<6} {'ACAO':<25} {'ACAC':<5} {'JSON?'}"
        print(f"{Style.BRIGHT}{Fore.WHITE}{header}")
        print(f"{Style.DIM}{'─'*100}")
    
    origin, method, status, acao, acac, json_possible = row
    # Color para la columna ACAO
    acao_color = Fore.RED if (acao in {"*", "null"} or "evil.com" in acao or "attacker.com" in acao) else Fore.YELLOW if acao else Fore.GREEN
    # Color para el estado
    status_color = Fore.GREEN if status == 200 else Fore.YELLOW if str(status).startswith(("2", "3")) else Fore.RED
    line = (f"{Fore.WHITE}{origin:<30} {method:<7} {status_color}{status:<6} "
            f"{acao_color}{acao:<25} {Fore.WHITE}{acac:<5} "
            f"{Fore.RED+'✓' if json_possible else Fore.GREEN+'✗'}")
    print(line)

def scan_cors(url):
    """Re-written scan routine with compact output."""
    try:
        print(BANNER)

        # ------------- USER INPUT -------------
        url = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL objetivo: ").strip()
        if not url:
            print_status("Debe proporcionar una URL", "error")
            return

        verify_ssl = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Verificar SSL [n]: ").strip().lower() == 'y'
        timeout = int(input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (10s): ").strip() or 10)

        custom_headers = None
        if input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}¿Headers personalizados? [n]: ").strip().lower() == 'y':
            headers = []
            print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Introduzca headers (Key: Value), ENTER vacío para terminar:")
            while True:
                h = input().strip()
                if not h:
                    break
                headers.append(h)
            custom_headers = parse_headers(headers)

        if not validate_url(url, verify_ssl, timeout):
            return

        # ------------- SESSION -------------
        session = requests.Session()
        session.verify = verify_ssl
        if not verify_ssl:
            session.trust_env = False
        if custom_headers:
            session.headers.update(custom_headers)

        # ------------- TEST CONFIG -------------
        test_origins = [
            'https://evil.com', 'http://evil.com', 'https://attacker.com',
            'https://example.com', 'http://example.com', 'https://subdomain.evil.com',
            'http://localhost', 'https://localhost', 'https://127.0.0.1', 'http://127.0.0.1'
        ]
        methods = ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE', 'PATCH']

        # Containers for results
        vuln_counter = defaultdict(int)
        printed_header = False

        # Wildcard subdomain quick test
        print_status("Probando vulnerabilidades de subdominios wildcard...", "info")
        wildcard_vuln, wildcard_origin = check_subdomain_vulnerability(url, verify_ssl, timeout)
        if wildcard_vuln:
            vuln_counter[f"Vulnerabilidad wildcard subdominio: {wildcard_origin}"] += 1

        # ------------- MAIN LOOP -------------
        print_header("ANÁLISIS CORS")

        for origin in test_origins:
            for method in methods:
                try:
                    if method == 'OPTIONS':
                        resp = session.options(url, headers={'Origin': origin}, timeout=timeout)
                    else:
                        resp = session.request(method, url, headers={'Origin': origin}, timeout=timeout)

                    acao = resp.headers.get('Access-Control-Allow-Origin', '')
                    acac = resp.headers.get('Access-Control-Allow-Credentials', '')
                    ctype = resp.headers.get('Content-Type', '')

                    json_possible = bool('json' in ctype.lower() and acao and (acao == '*' or ('evil.com' in acao or 'attacker.com' in acao) and acac == 'true'))

                    # Imprimir fila inmediatamente
                    row_data = (origin, method, resp.status_code, acao, acac, json_possible)
                    print_method_table_row(row_data, first_row=not printed_header)
                    printed_header = True

                    # --- collect unique issues ---
                    if acao == origin and origin != 'null':
                        vuln_counter["Origen reflejado sin validación"] += 1
                    if acao == '*' and acac == 'true':
                        vuln_counter["Configuración peligrosa: ACAO=* + ACAC=true"] += 1
                    if acao == 'null':
                        vuln_counter["Configuración peligrosa: ACAO=null"] += 1
                    if json_possible:
                        vuln_counter["JSON hijacking posible"] += 1
                    # add more rules here if desired …

                except requests.RequestException:
                    continue

        # ------------- OUTPUT -------------
        if printed_header:
            print(f"{Style.BRIGHT}{Fore.CYAN}{'─'*100}\n")

        # ------------- SUMMARY -------------
        print_header("RESUMEN DE VULNERABILIDADES")
        if vuln_counter:
            for vuln, count in vuln_counter.items():
                print_status(f"{vuln}  ({count} veces)", "error", prefix="!")
            print(f"\n{Style.BRIGHT}{Fore.RED}¡La web {url} es vulnerable a CORS!{Style.RESET_ALL}")
        else:
            print_status("No se detectaron vulnerabilidades CORS", "success")
            print(f"\n{Style.BRIGHT}{Fore.GREEN}La web {url} no es vulnerable a CORS{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print_status("Escaneo interrumpido por el usuario", "error")
        sys.exit(1)
