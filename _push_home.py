import subprocess
import sys
import socket
import os
from datetime import datetime

HOME_HOSTS = {"main", "Administrator"}  # Home PC hostname / username

def get_location():
    hostname = socket.gethostname()
    username = os.getlogin()
    if hostname in HOME_HOSTS or username in HOME_HOSTS:
        return "Home"
    return "Office"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def main():
    location = get_location()
    message = sys.argv[1] if len(sys.argv) > 1 else f"[{location}] {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print(f"Location : {location}")
    print(f"Message  : {message}")

    run("git add .")
    code = run(f'git commit -m "{message}"')
    if code != 0:
        print("Nothing to commit or commit failed.")
        return

    code = run("git push origin main")
    if code == 0:
        print("Push complete!")
    else:
        print("Push failed. Check the error above.")

if __name__ == "__main__":
    main()
