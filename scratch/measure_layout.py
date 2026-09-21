import subprocess
import time
import http.server
import socketserver
import threading
import os

PORT = 8098
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

# Let's inspect the layout at window-size=390,844
test_html = os.path.join(DIRECTORY, "scratch", "test_layout_measure.html")
with open(test_html, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<body>
<iframe id="f" src="../index.html" style="width:100%; border:none;"></iframe>
<script>
window.onload = () => {
  setTimeout(() => {
    const doc = document.getElementById('f').contentDocument;
    const win = document.getElementById('f').contentWindow;
    const c = doc.querySelector('.app-container');
    const hero = doc.querySelector('.streak-hero');
    const streak = doc.getElementById('streakCount');
    const weekly = doc.querySelector('.weekly-tracker');
    const footer = doc.querySelector('.stats-footer');
    
    console.log("VIEWPORT:", win.innerWidth, win.innerHeight);
    console.log("CONTAINER:", c.getBoundingClientRect());
    console.log("HERO:", hero.getBoundingClientRect());
    console.log("STREAK:", streak.getBoundingClientRect());
    console.log("WEEKLY:", weekly.getBoundingClientRect());
    console.log("FOOTER:", footer.getBoundingClientRect());
    document.body.innerHTML = `
      <div id="out">
        VIEWPORT: ${win.innerWidth} x ${win.innerHeight} <br>
        CONTAINER: left=${c.getBoundingClientRect().left}, width=${c.getBoundingClientRect().width}, right=${c.getBoundingClientRect().right} <br>
        WEEKLY: left=${weekly.getBoundingClientRect().left}, width=${weekly.getBoundingClientRect().width}, right=${weekly.getBoundingClientRect().right} <br>
        FOOTER: left=${footer.getBoundingClientRect().left}, width=${footer.getBoundingClientRect().width}, right=${footer.getBoundingClientRect().right}
      </div>
    `;
  }, 300);
};
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
    f"http://localhost:{PORT}/scratch/test_layout_measure.html"
]

proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
print(proc.stdout)
server.shutdown()
