import subprocess
import time
import http.server
import socketserver
import threading
import os
import json

PORT = 8130
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

print("=== PWA VERIFICATION SUITE ===")
all_passed = True

def check(condition, desc):
    global all_passed
    if condition:
        print(f"[OK] PASS: {desc}")
    else:
        print(f"[ERROR] FAIL: {desc}")
        all_passed = False


# 1. Test manifest.json
manifest_path = os.path.join(DIRECTORY, "manifest.json")
check(os.path.exists(manifest_path), "manifest.json exists")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

check(manifest.get("name") == "STREAK", "manifest name is STREAK")
check(manifest.get("short_name") == "STREAK", "manifest short_name is STREAK")
check(manifest.get("display") == "standalone", "manifest display is standalone")
check(manifest.get("theme_color") == "#0B1120", "manifest theme_color is #0B1120")
check(manifest.get("background_color") == "#0B1120", "manifest background_color is #0B1120")
check(len(manifest.get("icons", [])) >= 2, "manifest contains icons")

for icon in manifest.get("icons", []):
    src = icon["src"].replace("./", "")
    ipath = os.path.join(DIRECTORY, src)
    check(os.path.exists(ipath) and os.path.getsize(ipath) > 0, f"Icon file exists: {icon['src']} ({icon['sizes']}, {icon.get('purpose', 'any')})")

# 2. Test service-worker.js static assets
sw_path = os.path.join(DIRECTORY, "service-worker.js")
check(os.path.exists(sw_path), "service-worker.js exists")
with open(sw_path, "r", encoding="utf-8") as f:
    sw_code = f.read()
check("streak-pwa-v1" in sw_code, "service-worker.js defines cache key streak-pwa-v1")
check("cache.addAll" in sw_code, "service-worker.js pre-caches assets")
check("caches.match" in sw_code, "service-worker.js implements cache-first strategy")

# 3. Test in Headless Chrome via HTTP Server
class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    def log_message(self, format, *args):
        pass

server = socketserver.TCPServer(("", PORT), SilentHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
time.sleep(0.3)

# Test runner page for ServiceWorker and CacheStorage
sw_test_html = os.path.join(DIRECTORY, "scratch", "test_sw_cache.html")
with open(sw_test_html, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<body>
<div id="status">Testing...</div>
<script>
async function run() {
  const out = [];
  try {
    if (!('serviceWorker' in navigator)) {
      out.push('FAIL: ServiceWorker not supported');
      document.getElementById('status').innerText = out.join('\n');
      return;
    }
    const reg = await navigator.serviceWorker.register('../service-worker.js');
    out.push('PASS: ServiceWorker registered successfully');

    // Wait briefly for install and activation
    await new Promise(r => setTimeout(r, 1200));

    const cacheNames = await caches.keys();
    if (cacheNames.includes('streak-pwa-v1')) {
      out.push('PASS: Cache streak-pwa-v1 found in CacheStorage');
      const cache = await caches.open('streak-pwa-v1');
      const keys = await cache.keys();
      out.push(`PASS: Cache contains ${keys.length} cached resources`);
    } else {
      out.push(`FAIL: Cache streak-pwa-v1 not found. Existing: ${cacheNames.join(', ')}`);
    }
  } catch (e) {
    out.push('FAIL: Error: ' + e.message);
  }
  document.getElementById('status').innerText = out.join('\n');
}
run();
</script>
</body>
</html>
""")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--dump-dom",
    "--virtual-time-budget=6000",
    f"http://localhost:{PORT}/scratch/test_sw_cache.html"
]


proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
server.shutdown()

dom = proc.stdout
print("\n--- ServiceWorker & CacheStorage Browser Test ---")
if '<div id="status">' in dom and '</div>' in dom:
    status_content = dom.split('<div id="status">')[1].split('</div>')[0]
    for line in status_content.splitlines():
        clean_line = line.strip()
        if clean_line:
            print(clean_line)
            if "FAIL:" in clean_line:
                all_passed = False
else:
    print("Could not find status div in DOM output")
    all_passed = False

if all_passed:
    print("\nALL PWA CHECKS PASSED!")
else:
    print("\nSOME PWA CHECKS FAILED!")

