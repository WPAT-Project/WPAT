import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}WORDPRESS VERSION DETECTOR {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

def detect_wp_version(url):
    print(BANNER)
    normalized_url = url.rstrip('/')
    version_sources = [
        {
            "type": "meta_tag",
            "url": normalized_url,
            "pattern": r"WordPress\s+(\d+\.\d+(?:\.\d+)?)",
            "field": "content"
        },
        {
            "type": "rss",
            "url": f"{normalized_url}/feed/",
            "pattern": r"<generator>https://wordpress\.org/\?v=(\d+\.\d+(?:\.\d+)?)</generator>"
        },
        {
            "type": "readme",
            "url": f"{normalized_url}/readme.html",
            "pattern": r"Version\s+(\d+\.\d+(?:\.\d+)?)"
        },
        {
            "type": "css",
            "url": f"{normalized_url}/wp-includes/css/dist/block-library/style.min.css",
            "pattern": r"ver=(\d+\.\d+(?:\.\d+)?)"
        },
        {
            "type": "js",
            "url": f"{normalized_url}/wp-includes/js/wp-embed.min.js",
            "pattern": r"ver=(\d+\.\d+(?:\.\d+)?)"
        },
        # Nueva fuente añadida
        {
            "type": "opml",
            "url": f"{normalized_url}/wp-links-opml.php",
            "pattern": r'generator="WordPress/(\d+\.\d+(?:\.\d+)?)"'
        }
    ]

    detected_versions = []
    
    for source in version_sources:
        try:
            response = requests.get(
                source["url"],
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36"
                },
                allow_redirects=True
            )
            
            if response.status_code == 200:
                if source["type"] == "meta_tag":
                    soup = BeautifulSoup(response.text, 'html.parser')
                    meta = soup.find('meta', {'name': 'generator'})
                    if meta and (content := meta.get("content", "")):
                        match = re.search(source["pattern"], content)
                        if match:
                            detected_versions.append(match.group(1))
                else:
                    match = re.search(source["pattern"], response.text)
                    if match:
                        detected_versions.append(match.group(1))
                        
        except Exception as e:
            continue

    if detected_versions:
        final_version = max(set(detected_versions), key=detected_versions.count)
        print(f"{Fore.GREEN}[DETECTADA] Versión: {Style.BRIGHT}{final_version}")
    else:
        print(f"{Fore.RED}[NO DETECTADA] Versión no encontrada")
