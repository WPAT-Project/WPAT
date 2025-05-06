#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlparse
import urllib3
from colorama import init, Fore, Style

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

def print_method_result(method, status_code, acao, acac, content_type=None):
    """Imprime los resultados de una prueba de método"""
    print(f"\n{Style.BRIGHT}{Fore.YELLOW}▶ {method}")
    print(f"{Style.DIM}{'─'*30}")
    
    status_color = Fore.GREEN if status_code == 200 else Fore.YELLOW
    acao_color = Fore.RED if acao == 'https://evil.com' else Fore.WHITE
    acac_color = Fore.RED if acac == 'true' else Fore.WHITE
    
    print(f"{Style.BRIGHT}Estado: {status_color}{status_code}")
    print(f"{Style.BRIGHT}ACAO: {acao_color}{acao}")
    print(f"{Style.BRIGHT}ACAC: {acac_color}{acac}")
    
    if content_type:
        print(f"{Style.BRIGHT}Tipo de Contenido: {Fore.WHITE}{content_type}")

def check_dangerous_configs(headers):
    """Verifica configuraciones CORS peligrosas"""
    vulnerabilities = []
    
    if headers.get('Access-Control-Allow-Origin') == '*' and headers.get('Access-Control-Allow-Credentials') == 'true':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Origin: * con Access-Control-Allow-Credentials: true")
    
    if headers.get('Access-Control-Allow-Headers') == '*':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Headers: *")
    
    if headers.get('Access-Control-Allow-Origin') == 'null':
        vulnerabilities.append("Configuración peligrosa: Access-Control-Allow-Origin: null")
    
    if headers.get('Access-Control-Allow-Origin') and headers.get('Access-Control-Allow-Origin') != '*':
        vulnerabilities.append("Posible origen reflejado sin validación")
    
    return vulnerabilities

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
        
        if response.status_code != 200:
            print_status(f"La URL devuelve código de estado {response.status_code}", "warning")
            return False
            
        headers = {
            'Origin': 'https://evil.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            options_response = session.options(url, headers=headers, timeout=timeout)
            cors_headers = {
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers',
                'Access-Control-Allow-Credentials',
                'Access-Control-Max-Age'
            }
            
            if any(header in options_response.headers for header in cors_headers):
                print_status("URL válida para análisis CORS", "success")
                return True
            else:
                print_status("La URL no tiene configuraciones CORS", "warning")
                return False
        except:
            print_status("No se pudo verificar CORS", "warning")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"Error de conexión: {str(e)}", "error")
        return False
    except Exception as e:
        print_status(f"Error inesperado: {str(e)}", "error")
        return False

def scan_cors(url):
    """Realiza el escaneo CORS de la URL"""
    try:
        print(BANNER)
        
        # Obtener URL objetivo
        print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL objetivo: ", end="")
        url = input().strip()
        
        # Obtener preferencia de verificación SSL
        print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Verificar SSL [n]: ", end="")
        verify_ssl = input().strip().lower() == 'y'
        
        # Obtener timeout
        print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Timeout (10s): ", end="")
        timeout_input = input().strip()
        timeout = int(timeout_input) if timeout_input else 10
        
        # Obtener headers personalizados
        custom_headers = None
        print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Añadir cabeceras personalizadas? [n]: ", end="")
        if input().strip().lower() == 'y':
            headers = []
            print(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Introduzca las cabeceras (una por línea, vacío para terminar):")
            while True:
                header = input().strip()
                if not header:
                    break
                headers.append(header)
            custom_headers = parse_headers(headers)
        
        if not validate_url(url, verify_ssl, timeout):
            return

        session = requests.Session()
        session.verify = verify_ssl
        if not verify_ssl:
            session.trust_env = False
        if custom_headers:
            session.headers.update(custom_headers)

        headers = {
            'Origin': 'https://evil.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        methods = ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']
        vulnerabilities = []
        
        print_header("ANÁLISIS CORS")
        print(f"{Fore.WHITE}URL: {url}")

        for method in methods:
            try:
                if method == 'OPTIONS':
                    response = session.options(url, headers=headers, timeout=timeout)
                else:
                    response = session.request(method, url, headers=headers, timeout=timeout)
                
                acao = response.headers.get('Access-Control-Allow-Origin')
                acac = response.headers.get('Access-Control-Allow-Credentials')
                content_type = response.headers.get('Content-Type', '')
                
                if response.status_code == 200 or 'Access-Control-Allow-Origin' in response.headers:
                    print_method_result(method, response.status_code, acao, acac, content_type)
                    
                    # Verificar configuraciones peligrosas
                    dangerous_configs = check_dangerous_configs(response.headers)
                    for config in dangerous_configs:
                        vulnerabilities.append(f"{config} ({method})")
                    
                    if acao == '*':
                        vulnerabilities.append(f"Origen permitido: * ({method})")
                    elif acao == 'https://evil.com':
                        vulnerabilities.append(f"Origen reflejado: evil.com ({method})")
                    elif acac == 'true' and (acao == '*' or acao == 'https://evil.com'):
                        vulnerabilities.append(f"Credenciales con origen inseguro ({method})")
                
            except requests.exceptions.RequestException:
                continue

        # Imprimir resumen
        print_header("RESUMEN")
        
        if vulnerabilities:
            print_status("VULNERABILIDADES DETECTADAS:", "error")
            for vuln in set(vulnerabilities):
                print_status(vuln, "error", prefix="!")
            print(f"\n{Style.BRIGHT}{Fore.RED}La web {url} es vulnerable a CORS{Style.RESET_ALL}")
        else:
            print_status("No se detectaron vulnerabilidades CORS", "success")
            print(f"\n{Style.BRIGHT}{Fore.GREEN}La web {url} no es vulnerable a CORS{Style.RESET_ALL}")

    except Exception as e:
        print_status(f"Error: {str(e)}", "error")

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