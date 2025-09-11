import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, TooManyRedirects
from json import JSONDecodeError
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}REST API SECURITY AUDITOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def print_status(message, status, extra_info=""):
    status_colors = {
        "safe": Fore.GREEN,
        "warning": Fore.YELLOW,
        "danger": Fore.RED,
        "info": Fore.CYAN,
        "critical": Fore.MAGENTA + Style.BRIGHT
    }
    status_symbols = {
        "safe": "✓",
        "warning": "⚠",
        "danger": "✗",
        "info": "ℹ",
        "critical": "☠"
    }
    print(f"{status_colors[status]}{status_symbols[status]} {status.upper():<9} {Fore.WHITE}{message} {extra_info}")

def print_section_header(title, severity):
    severity_colors = {
        "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
        "HIGH": Fore.RED + Style.BRIGHT,
        "MEDIUM": Fore.YELLOW + Style.BRIGHT,
        "LOW": Fore.CYAN + Style.BRIGHT
    }
    
    # Define a minimum width for the box
    min_box_width = 30  # Minimum box width
    
    # Calculate the required box width depending on the title
    title_length = len(title)
    box_width = max(min_box_width, title_length + 4)  # The box must be at least as wide as the title, with 2 spaces on each side
    
    # Calculate the available space to center the text
    padding_left = (box_width - 2 - title_length) // 2  # Calculate the space on the left
    padding_right = box_width - 2 - title_length - padding_left  # The remaining space goes to the right
    
    # Print the box with the centered title
    print(f"\n{severity_colors[severity]}┌{'─' * (box_width - 2)}┐")
    print(f"│{' ' * padding_left}{title}{' ' * padding_right}│")
    print(f"└{'─' * (box_width - 2)}┘{Style.RESET_ALL}")

def check_rest_api(url):
    print(BANNER)
    target_url = url.rstrip("/") + "/"
    print_status(f"Scanning target:", "info", f"{Fore.YELLOW}{target_url}")
    
    # Endpoints classified by expected severity
    endpoints_by_severity = {
        "CRITICAL": [
            {"path": "/wp-json/wp/v2/users", "description": "Exposed user list"},
            {"path": "/wp-json/wp/v2/users/me", "description": "Authenticated user information"},
        ],
        "HIGH": [
            {"path": "/wp-json/wp/v2/comments", "description": "Public comments"},
            {"path": "/wp-json/wp/v2/media", "description": "Public media files (images, PDFs, etc.)"},
            {"path": "/wp-json/wp/v2/search", "description": "Content search functionality"},
        ],
        "MEDIUM": [
            {"path": "/wp-json/wp/v2/posts", "description": "Public posts listing"},
            {"path": "/wp-json/wp/v2/pages", "description": "Public pages listing"},
            {"path": "/wp-json/wp/v2/categories", "description": "Categories listing"},
            {"path": "/wp-json/wp/v2/tags", "description": "Tags listing"},
        ],
        "LOW": [
            {"path": "/wp-json/", "description": "API root endpoint"},
            {"path": "/wp-json/wp/v2", "description": "WP namespace root"},
            {"path": "/wp-json/wp/v2/types", "description": "Content types information"},
            {"path": "/wp-json/wp/v2/statuses", "description": "Content statuses"},
            {"path": "/wp-json/wp/v2/taxonomies", "description": "Registered taxonomies"},
            {"path": "/wp-json/wp/v2/block-types", "description": "Available block types"},
            {"path": "/wp-json/oembed/1.0", "description": "oEmbed root endpoint"},
            {"path": "/wp-json/oembed/1.0/embed", "description": "oEmbed metadata"},
        ]
    }
    
    # Counters for summary
    results_summary = {
        "critical": 0,
        "danger": 0,
        "warning": 0,
        "safe": 0
    }
    
    # Function to check a single endpoint
    def check_endpoint(endpoint, severity):
        try:
            full_url = f"{target_url}{endpoint.lstrip('/')}"
            response = requests.get(
                full_url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36'},
                allow_redirects=False
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        if isinstance(data, list):
                            item_count = len(data)
                            plural = "s" if item_count != 1 else ""
                            detail = f"{Fore.WHITE}({item_count} item{plural})"
                            
                            # Determine status based on content and severity
                            if severity == "CRITICAL":
                                status = "critical"
                                results_summary["critical"] += 1
                            else:
                                status = "danger"
                                results_summary["danger"] += 1
                        else:
                            # It's a dictionary, not a list
                            key_count = len(data.keys())
                            plural = "s" if key_count != 1 else ""
                            detail = f"{Fore.WHITE}({key_count} key{plural})"
                            status = "warning"
                            results_summary["warning"] += 1
                            
                        print_status(f"{endpoint}", status, detail)
                    else:
                        print_status(f"{endpoint}", "warning", f"{Fore.YELLOW}(empty response)")
                        results_summary["warning"] += 1
                except JSONDecodeError:
                    print_status(f"{endpoint}", "warning", f"{Fore.YELLOW}(non-JSON response)")
                    results_summary["warning"] += 1
            else:
                # For non-200 status codes, mark as safe
                print_status(f"{endpoint}", "safe", f"{Fore.GREEN}(HTTP {response.status_code})")
                results_summary["safe"] += 1
                
        except Timeout:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}(request timeout)")
            results_summary["danger"] += 1
        except ConnectionError:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}(connection failed)")
            results_summary["danger"] += 1
        except TooManyRedirects:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}(too many redirects)")
            results_summary["danger"] += 1
        except RequestException as e:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}(request error)")
            results_summary["danger"] += 1
        except Exception as e:
            print_status(f"{endpoint}", "danger", f"{Fore.RED}(unexpected error: {type(e).__name__})")
            results_summary["danger"] += 1
            
        return True
    
    # Scan endpoints by severity order (highest to lowest)
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        print_section_header(f"{severity} SEVERITY ENDPOINTS", severity)
        
        for endpoint_info in endpoints_by_severity[severity]:
            endpoint = endpoint_info["path"]
            description = endpoint_info["description"]
            
            # Add parameters to endpoints that need them
            if endpoint == "/wp-json/wp/v2/search":
                endpoint += "?search=hello"
            elif endpoint == "/wp-json/wp/v2/posts":
                endpoint += "?per_page=1"
            
            # Print description with appropriate color
            severity_colors = {
                "CRITICAL": Fore.MAGENTA,
                "HIGH": Fore.RED,
                "MEDIUM": Fore.YELLOW,
                "LOW": Fore.CYAN
            }
            print(f"{severity_colors[severity]}    • {description}:")
            check_endpoint(endpoint, severity)

    # Summary
    print(f"\n{Fore.CYAN}{Style.BRIGHT}┌{'─' * 70}┐")
    text = "SCAN SUMMARY"
    total_width = 70
    spaces = (total_width - len(text) - 2) // 2  # Restamos 2 por los espacios del borde │
    print(f"{Fore.CYAN}│ {' ' * spaces}{Fore.WHITE}{text}{' ' * (total_width - len(text) - spaces - 2)}{Fore.CYAN} │")
    print(f"{Fore.CYAN}├{'─' * 70}┤{Fore.WHITE}")
    
    # Format summary lines with proper alignment
    critical_text = f"☠ Critical: {results_summary['critical']} endpoints with highly sensitive data exposed"
    danger_text = f"✗ Dangerous: {results_summary['danger']} endpoints with significant data exposure"
    warning_text = f"⚠ Warning: {results_summary['warning']} endpoints with limited data or access issues"
    safe_text = f"✓ Safe: {results_summary['safe']} endpoints with no concerning data exposure"
    
    print(f"│ {Fore.MAGENTA}{critical_text.ljust(68)} {Fore.WHITE}│")
    print(f"│ {Fore.RED}{danger_text.ljust(68)} {Fore.WHITE}│")
    print(f"│ {Fore.YELLOW}{warning_text.ljust(68)} {Fore.WHITE}│")
    print(f"│ {Fore.GREEN}{safe_text.ljust(68)} {Fore.WHITE}│")
    print(f"└{'─' * 70}┘")
