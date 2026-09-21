import subprocess
import time
import http.server
import socketserver
import threading
import os

PORT = 8099
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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

test_html = os.path.join(DIRECTORY, "scratch", "test_direct_measure.html")
with open(test_html, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <div class="app-container">
    <header class="app-header">
      <h1 class="app-title">Streak</h1>
    </header>
    <main class="app-main">
      <div class="streak-hero">
        <span class="streak-count">12</span>
      </div>
      <div class="weekly-tracker">
        <div class="weekly-grid">
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
          <div class="weekly-day"><span class="weekly-dot"></span></div>
        </div>
      </div>
    </main>
    <footer class="stats-footer">
      <div class="stat-item"><span>Best streak</span><span>18 days</span></div>
    </footer>
  </div>
  <div id="metrics" style="position:fixed; bottom:0; left:0; background:white; color:black; font-size:12px; z-index:9999;"></div>
  <script>
    window.addEventListener('load', () => {
      const c = document.querySelector('.app-container');
      const w = document.querySelector('.weekly-tracker');
      const f = document.querySelector('.stats-footer');
      const m = document.getElementById('metrics');
      m.innerHTML = `WINDOW: ${window.innerWidth} x ${window.innerHeight} | BODY: ${document.body.offsetWidth} | CONTAINER: ${c.offsetWidth} (left=${c.getBoundingClientRect().left}, right=${c.getBoundingClientRect().right}) | WEEKLY: ${w.offsetWidth} (left=${w.getBoundingClientRect().left}, right=${w.getBoundingClientRect().right}) | FOOTER: ${f.offsetWidth} (left=${f.getBoundingClientRect().left}, right=${f.getBoundingClientRect().right}) | SCROLLWIDTH: ${document.documentElement.scrollWidth}`;
    });
  </script>
</body>
</html>
""")

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=390,844",
    "--dump-dom",
    "--virtual-time-budget=1000",
    f"http://localhost:{PORT}/scratch/test_direct_measure.html"
]

proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
for line in proc.stdout.splitlines():
    if "WINDOW:" in line:
        print(line.strip())
server.shutdown()
