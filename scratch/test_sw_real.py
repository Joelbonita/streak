import subprocess
import time
import http.server
import socketserver
import threading
import os
import urllib.request
import json

PORT = 8135
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

# Create a test page that synchronous-evaluates or tests caches directly
test_page = os.path.join(DIRECTORY, "scratch", "sw_check.html")
with open(test_page, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<body>
  <div id="log">START</div>
  <script>
    navigator.serviceWorker.register('../service-worker.js').then(reg => {
      document.getElementById('log').innerHTML += '<br>REGISTERED: ' + reg.scope;
      return caches.open('streak-pwa-v1');
    }).then(cache => {
      document.getElementById('log').innerHTML += '<br>CACHE_OPENED';
      return cache.addAll([
        '../index.html',
        '../css/style.css',
        '../js/Streak.js',
        '../js/StreakStorage.js',
        '../js/app.js',
        '../manifest.json'
      ]);
    }).then(() => {
      document.getElementById('log').innerHTML += '<br>ASSETS_CACHED_SUCCESS';
    }).catch(err => {
      document.getElementById('log').innerHTML += '<br>ERR: ' + err.message;
    });
  </script>
</body>
</html>
""")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = os.path.join(DIRECTORY, "scratch", "chrome_profile")
os.makedirs(user_data_dir, exist_ok=True)

# Launch chrome with remote debugging port to inspect output
proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    f"--user-data-dir={user_data_dir}",
    "--remote-debugging-port=9222",
    f"http://localhost:{PORT}/scratch/sw_check.html"
])

# Poll via CDP HTTP endpoint
time.sleep(2.5)

try:
    req = urllib.request.urlopen("http://localhost:9222/json")
    tabs = json.loads(req.read().decode())
    print("Chrome tabs open:", len(tabs))
    for t in tabs:
        print("Tab:", t.get("title"), t.get("url"))
finally:
    proc.terminate()
    server.shutdown()

# Now run dump-dom with the populated user data dir!
dump_proc = subprocess.run([
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    f"--user-data-dir={user_data_dir}",
    "--dump-dom",
    f"http://localhost:{PORT}/scratch/sw_check.html"
], capture_output=True, text=True, timeout=10)

print("\nDOM Output from user profile:")
for line in dump_proc.stdout.splitlines():
    if "REGISTERED" in line or "CACHE" in line or "ERR" in line:
        print(line.strip())
