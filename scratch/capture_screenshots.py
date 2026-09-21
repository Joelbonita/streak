import subprocess
import time
import http.server
import socketserver
import threading
import os
import json

PORT = 8095
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACT_DIR = r"C:\Users\WINDOWS 10\.gemini\antigravity\brain\0b3ccf88-423c-42b1-bbcc-6bb39fe2dc1b"

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    def log_message(self, format, *args):
        pass

def run_server():
    server = socketserver.TCPServer(("", PORT), SilentHandler)
    server.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(0.5)

# Create a demo page that sets up the exact mock data from the prompt specification
demo_html_path = os.path.join(DIRECTORY, "scratch", "demo_showcase.html")
with open(demo_html_path, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script>
    // Seed localStorage with the prompt's reference streak state
    const demoData = {
      name: "LEARNING C#",
      currentStreak: 12,
      bestStreak: 18,
      startDate: "2026-09-10",
      lastCheckInDate: "2026-09-20", // Checked in yesterday (2026-09-20), today is 2026-09-21
      history: [
        "2026-09-10", "2026-09-11", "2026-09-12", "2026-09-13",
        "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17",
        "2026-09-18", "2026-09-19", "2026-09-20"
      ]
    };
    localStorage.setItem("streak_app_data_v1", JSON.stringify(demoData));
    window.location.replace("../index.html");
  </script>
</head>
<body></body>
</html>
""")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
target_url = f"http://localhost:{PORT}/scratch/demo_showcase.html"

viewports = [
    ("mobile_390", 390, 844),
    ("mobile_360", 360, 780),
    ("mobile_430", 430, 932),
    ("desktop_1200", 1200, 850)
]

for name, w, h in viewports:
    out_img = os.path.join(ARTIFACT_DIR, f"screenshot_{name}.png")
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={out_img}",
        "--virtual-time-budget=2000",
        target_url
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    print(f"Captured {name}: {out_img} (exists: {os.path.exists(out_img)})")

print("All screenshots generated successfully.")
