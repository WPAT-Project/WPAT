# ssl_checker.py
import ssl
import socket
import re
from datetime import datetime, timezone
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}SSL/TLS CERTIFICATE AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
{Style.RESET_ALL}"""

def print_status(message, status, extra_info=""):
    status_colors = {
        "safe": Fore.GREEN,
        "warning": Fore.YELLOW,
        "danger": Fore.RED,
        "info": Fore.CYAN
    }
    print(f"{status_colors[status]}{Style.BRIGHT}[{status.upper()}] {Fore.WHITE}{message} {extra_info}")

def clean_domain(domain):
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    return domain.rstrip('/').strip()

def check_ssl(url):
    print(BANNER)
    domain = clean_domain(url)
    
    if not domain:
        print_status("Error: Dominio inválido", "danger")
        return None

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expire_date = datetime.strptime(
                    cert['notAfter'], 
                    "%b %d %H:%M:%S %Y GMT"
                ).replace(tzinfo=timezone.utc)
                
                current_date = datetime.now(timezone.utc)
                is_expired = expire_date < current_date
                issuer = next(
                    (dict(field)['commonName'] 
                     for field in cert['issuer'] 
                     if 'commonName' in dict(field)),
                    "Desconocido"
                )

                # Resultados con formato
                print_status("Objetivo escaneado", "info", f"{Fore.YELLOW}{domain}")
                print_status("Protocolo", "info", f"{Fore.CYAN}{ssock.version()}")
                print_status("Cifrado activo", "info", f"{Fore.CYAN}{ssock.cipher()[0]}")
                print_status("Emisor certificado", "info", f"{Fore.CYAN}{issuer}")
                print_status("Expiración", 
                           "warning" if is_expired else "safe", 
                           f"{Fore.YELLOW if is_expired else Fore.GREEN}{expire_date.strftime('%d/%m/%Y')}")
                print_status("Estado certificado", 
                           "danger" if is_expired else "safe", 
                           f"{Fore.RED}EXPIRADO" if is_expired else f"{Fore.GREEN}VÁLIDO")

                return {
                    'domain': domain,
                    'protocol': ssock.version(),
                    'cipher': ssock.cipher()[0],
                    'issuer': issuer,
                    'expiration': expire_date,
                    'is_expired': is_expired
                }

    except socket.timeout:
        print_status("Error: Timeout de conexión", "danger")
    except Exception as e:
        print_status("Error crítico", "danger", f"{Fore.RED}{str(e)}")
    
    return None