import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS VERSION DETECTOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def detect_wp_version(url):
    print(BANNER)
    version_sources = [
        {"type": "meta_tag", "url": f"{url}", "pattern": r"WordPress (\d+\.\d+\.\d+)"},
        {"type": "readme", "url": f"{url}/readme.html", "pattern": r"Version (\d+\.\d+)"},
        {"type": "css", "url": f"{url}/wp-includes/css/dist/block-library/style.min.css", "pattern": r"ver=(\d+\.\d+\.\d+)"},
        {"type": "js", "url": f"{url}/wp-includes/js/wp-embed.min.js", "pattern": r"ver=(\d+\.\d+\.\d+)"}
    ]

    detected_versions = []
    
    for source in version_sources:
        try:
            response = requests.get(source["url"], timeout=5, headers={'User-Agent': 'WP Audit Tool'})
            if response.status_code == 200:
                if source["type"] == "meta_tag":
                    soup = BeautifulSoup(response.text, 'html.parser')
                    meta = soup.find('meta', {'name': 'generator'})
                    if meta and 'WordPress' in meta['content']:
                        version = re.search(source["pattern"], meta['content']).group(1)
                        detected_versions.append(version)
                
                else:
                    match = re.search(source["pattern"], response.text)
                    if match:
                        detected_versions.append(match.group(1))
        except:
            continue

    if detected_versions:
        final_version = max(set(detected_versions), key=detected_versions.count)
        print(f"{Fore.GREEN}[DETECTADA] Versión: {Style.BRIGHT}{final_version}")
    else:
        print(f"{Fore.RED}[NO DETECTADA] Versión no encontrada")