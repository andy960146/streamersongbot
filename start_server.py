import subprocess
import threading
import time
import webbrowser
from queue_server import app
from main_core import run_main

def run_flask():
    app.run(host="0.0.0.0", port=8888)

def run_ngrok():
    ngrok_path = r"C:\ngrok-v3-stable-windows-amd64\ngrok.exe"  # 修改成你的ngrok.exe完整路徑！
    subprocess.Popen([ngrok_path, "http", "8888"])
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:4040")  # 自動打開ngrok控制台

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()   # 啟動Flask server
    threading.Thread(target=run_main).start()     # 啟動Twitch + Spotify主控
    time.sleep(1)
    run_ngrok()                                  # 開啟Ngrok
