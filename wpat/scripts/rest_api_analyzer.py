import requests
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}REST API SECURITY AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status, extra_info=""):
    status_colors = {
        "safe": Fore.GREEN,
        "warning": Fore.YELLOW,
        "danger": Fore.RED,
        "info": Fore.CYAN
    }
    print(f"{status_colors[status]}{Style.BRIGHT}[{status.upper()}] {Fore.WHITE}{message} {extra_info}")

def check_rest_api(url):
    print(BANNER)
    target_url = url.rstrip("/") + "/"
    print_status(f"Scanning REST API:", "info", Fore.YELLOW + target_url)
    
    endpoints = [
        "/wp-json/wp/v2/users",
        "/wp-json/wp/v2/posts?per_page=1",
        "/wp-json/wp/v2/comments",
        "/wp-json/wp/v2/settings",
        "/wp-json/wp/v2/taxonomies",
        "/wp-json/wp/v2/pages",
        "/wp-json/wp/v2/media",
        "/wp-json/wp/v2/categories",
        "/wp-json/wp/v2/tags",
        "/wp-json/wp/v2/types",
        "/wp-json/wp/v2/statuses",
    ]
    
    for endpoint in endpoints:
        try:
            full_url = f"{target_url}{endpoint.lstrip('/')}"
            response = requests.get(
                full_url,
                timeout=10,
                headers={'User-Agent': 'WP Audit Tool'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    detail = f"{Fore.YELLOW}({len(data) if isinstance(data, list) else 'data'})"
                    status = "danger" if isinstance(data, list) else "warning"
                    print_status(f"{endpoint}", status, detail)
                else:
                    print_status(f"{endpoint}", "warning", f"{Fore.YELLOW}(empty)")
            else:
                print_status(f"{endpoint}", "safe", f"{Fore.CYAN}(code {response.status_code})")
                
        except Exception as e:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}[Error: {str(e)}]")
