import subprocess
import time
import http.server
import socketserver
import threading
import os

PORT = 8110
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACT_DIR = r"C:\Users\WINDOWS 10\.gemini\antigravity\brain\0b3ccf88-423c-42b1-bbcc-6bb39fe2dc1b"

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    def log_message(self, format, *args):
        pass

server = socketserver.TCPServer(("", PORT), SilentHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
time.sleep(0.3)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def capture(url, out_name, w=520, h=880):
    out_file = os.path.join(ARTIFACT_DIR, out_name)
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={out_file}",
        "--virtual-time-budget=2000",
        url
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=12)
    print(f"Captured {out_name}: {os.path.exists(out_file)}")

capture(f"http://localhost:{PORT}/scratch/shot_main.html", "screenshot_main_screen.png", 520, 880)
capture(f"http://localhost:{PORT}/scratch/shot_checked.html", "screenshot_checked_in.png", 520, 880)
capture(f"http://localhost:{PORT}/scratch/shot_modal_open.html", "screenshot_modal.png", 520, 880)
capture(f"http://localhost:{PORT}/scratch/shot_main.html", "screenshot_desktop.png", 1080, 780)

server.shutdown()
