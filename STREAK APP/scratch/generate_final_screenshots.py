import subprocess
import time
import http.server
import socketserver
import threading
import os

PORT = 8105
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

# 1. Page for Main Screen (12 days streak, ready to check in today)
html_main = os.path.join(DIRECTORY, "scratch", "shot_main.html")
with open(html_main, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
  const data = {
    name: "LEARNING C#",
    currentStreak: 12,
    bestStreak: 18,
    startDate: "2026-09-10",
    lastCheckInDate: "2026-09-20", // yesterday
    history: [
      "2026-09-10", "2026-09-11", "2026-09-12", "2026-09-13",
      "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17",
      "2026-09-18", "2026-09-19", "2026-09-20"
    ]
  };
  localStorage.setItem("streak_app_data_v1", JSON.stringify(data));
  window.location.replace("../index.html");
</script>
</body>
</html>
""")

# 2. Page for Checked In State (13 days, Checked In disabled, today completed)
html_checked = os.path.join(DIRECTORY, "scratch", "shot_checked.html")
with open(html_checked, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
  const data = {
    name: "LEARNING C#",
    currentStreak: 13,
    bestStreak: 18,
    startDate: "2026-09-10",
    lastCheckInDate: "2026-09-21", // today (completed)
    history: [
      "2026-09-10", "2026-09-11", "2026-09-12", "2026-09-13",
      "2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17",
      "2026-09-18", "2026-09-19", "2026-09-20", "2026-09-21"
    ]
  };
  localStorage.setItem("streak_app_data_v1", JSON.stringify(data));
  window.location.replace("../index.html");
</script>
</body>
</html>
""")

# 3. Page for Edit Modal Open
html_modal = os.path.join(DIRECTORY, "scratch", "shot_modal.html")
with open(html_modal, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<script>
  const data = {
    name: "LEARNING C#",
    currentStreak: 12,
    bestStreak: 18,
    startDate: "2026-09-10",
    lastCheckInDate: "2026-09-20",
    history: ["2026-09-20"]
  };
  localStorage.setItem("streak_app_data_v1", JSON.stringify(data));
  window.location.replace("../index.html");
</script>
</body>
</html>
""")

def capture(url, out_name, w=540, h=900, post_js=None):
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
capture(f"http://localhost:{PORT}/scratch/shot_main.html", "screenshot_desktop.png", 1080, 780)

server.shutdown()
