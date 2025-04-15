import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
import re

init(autoreset=True)

BANNER = f"""
{Style.BRIGHT}{Fore.CYAN}
■▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀■
■ {Fore.WHITE}SENSITIVE FILES SCANNER {Fore.CYAN}■
■▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄■
"""

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
CONCURRENT_REQUESTS = 10
TIMEOUT = 8

FILE_CHECKS = {
    "wp-config.*": lambda c: "DB_NAME" in c and "DB_PASSWORD" in c,
    "wp-content/debug.log": lambda c: "PHP Notice" in c,
    "wp-admin/(install|upgrade).php": lambda c: "WordPress Installation" in c,
    ".env": lambda c: "APP_KEY" in c or "DATABASE_URL" in c,
    "web.config": lambda c: "<configuration>" in c,
    ".htaccess": lambda c: "RewriteEngine" in c,
    "error_log": lambda c: "[error]" in c.lower(),
    "access.log": lambda c: re.search(r'\d+\.\d+\.\d+\.\d+', c),
    "backup.*(sql|zip|tar.gz)": lambda c: len(c) > 1024,
    ".git/config": lambda c: "[core]" in c,
    ".svn/entries": lambda c: "dir" in c,
    "phpinfo.php": lambda c: "PHP Version" in c,
    "info.php": lambda c: "phpinfo()" in c,
    ".DS_Store": lambda c: b"Bud1" in c.encode(),
    "Thumbs.db": lambda c: b"\xFD\xFF\xFF\xFF" in c.encode()
}

def is_valid_response(content, filename):
    for pattern, check in FILE_CHECKS.items():
        regex_pattern = pattern.replace('.', r'\.').replace('*', r'.*')
        if re.match(regex_pattern, filename):
            return check(content)
    return len(content.strip()) > 200

def check_file(session, url, file):
    full_url = f"{url.rstrip('/')}/{file.lstrip('/')}"
    try:
        response = session.head(full_url, timeout=TIMEOUT)
        if response.status_code != 200:
            return (file, "PROTEGIDO", Fore.BLUE)
            
        response = session.get(full_url, timeout=TIMEOUT)
        content = response.text if response.headers.get('Content-Type', '').startswith('text/') else str(response.content)
        
        if is_valid_response(content, file):
            return (file, "EXPUESTO", Fore.GREEN)
        return (file, "POSIBLE FALSO POSITIVO", Fore.YELLOW)
            
    except requests.exceptions.RequestException:
        return (file, "ERROR", Fore.RED)

def scan_sensitive_files(url):
    print(BANNER)
    files = [
        "wp-config.php", "wp-config.php.bak", "wp-config.php.save", "wp-config.php~",
        ".htaccess", "web.config", "php.ini", ".user.ini", ".env",
        "debug.log", "wp-content/debug.log", "error_log", "wp-error.log",
        "wp-admin/install.php", "wp-admin/upgrade.php", "wp-admin/setup-config.php",
        "phpinfo.php", "info.php",
        "license.txt", "readme.html", "readme.txt",
        "wp-login.php", "wp-settings.php", "wp-load.php",
        "wp-includes/pluggable.php", "wp-includes/functions.php",
        "wp-content/plugins/", "wp-content/themes/", "wp-content/uploads/",
        "backup.zip", "backup.tar.gz", "backup.sql", "db_backup.sql",
        "wp-backup.php", "backup-wp-config.php", "wp-config.old", "wp-config.txt",
        "admin.php", "ajax.php", "upload.php", "settings.php", "connector.php",
        "sample-config.php", "wp-config-sample.php",
        ".git/config", ".svn/entries", ".DS_Store", "Thumbs.db",
        "wp-cron.php", "wp-trackback.php", "wp-comments-post.php",
        "error_log.1", "debug.log.1", "access_log", "access.log"
    ]
    
    print(f"{Fore.CYAN}[INFO] Escaneando {len(files)} archivos sensibles...")
    
    with requests.Session() as session:
        session.headers.update({'User-Agent': DEFAULT_USER_AGENT})
        session.max_redirects = 1
        
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = {executor.submit(check_file, session, url, f): f for f in files}
            
            for future in as_completed(futures):
                file, status, color = future.result()
                print(f"{color}[{status}] {file}")