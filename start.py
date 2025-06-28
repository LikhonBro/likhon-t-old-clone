import os
import sys
import json
import uuid
import hashlib
import datetime
import webbrowser
import subprocess

# === CONFIG ===
MAIN_TOOL = "Alpha_old-clone.py"
SUBS_FILE = "subs.json"
TELEGRAM_BOT_URL = "http://t.me/clone_tool_subscription_bot"

# === DEVICE ID & KEY GENERATION ===
def get_device_id():
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()[:16]

def get_key(device_id):
    salt = "CLONE_TOOL"
    return hashlib.sha256((device_id + salt).encode()).hexdigest().upper()

# === SUBSCRIPTION CHECK ===
def load_subs():
    if not os.path.exists(SUBS_FILE):
        return {}
    with open(SUBS_FILE, "r") as f:
        return json.load(f)

def is_subscribed(device_id, subs):
    info = subs.get(device_id)
    if not info:
        return False
    exp = datetime.datetime.strptime(info["expires"], "%Y-%m-%d")
    return exp >= datetime.datetime.now()

def show_interface(device_id, key):
    os.system("cls" if os.name == "nt" else "clear")
    print(r"""
 █████╗ ██╗     ██████╗ ██╗  ██╗ █████╗ 
██╔══██╗██║     ██╔══██╗██║  ██║██╔══██╗
███████║██║     ██████╔╝███████║███████║
██╔══██║██║     ██╔═══╝ ██╔══██║██╔══██║
██║  ██║███████╗██║     ██║  ██║██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
\x1b[1;95m╔═══════════════════════════════════════════════════════╗
\x1b[1;95m║\x1b[1;97m                ✦  𝗧𝗢𝗢𝗟 I𝗡𝗙𝗢 𝗣𝗔𝗡𝗘𝗟  ✦                  \x1b[1;95m║
\x1b[1;95m╚═══════════════════════════════════════════════════════╝
\x1b[1;96m   ➤ \x1b[1;97mCreator        : \x1b[1;96mLikhon 💡
\x1b[1;96m   ➤ \x1b[1;97mOperated By    : \x1b[1;92mALPHA \x1b[1;91m(\x1b[1;90mPremium Access\x1b[1;91m)
\x1b[1;96m   ➤ \x1b[1;97mTool Access    : \x1b[1;93mPAID
\x1b[1;96m   ➤ \x1b[1;97mCurrent Version: \x1b[1;95m0.2
\x1b[1;92m─────────────────────────────────────────────────────────""")
    print("\n[-] SENT THIS KEY FOR BUY TOOL")
    print(f"[-] PRESS ENTER TO OPEN TELEGRAM BOT ({TELEGRAM_BOT_URL})")
    input()
    webbrowser.open(TELEGRAM_BOT_URL)

def main():
    device_id = get_device_id()
    key = get_key(device_id)
    subs = load_subs()

    if not is_subscribed(device_id, subs):
        show_interface(device_id, key)
        sys.exit(0)

    # Subscription valid, launch main tool
    subprocess.run([sys.executable, MAIN_TOOL])

if __name__ == "__main__":
    main() 