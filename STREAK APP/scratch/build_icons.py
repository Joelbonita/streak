import subprocess
import time
import http.server
import socketserver
import threading
import os
import base64
import json

PORT = 8120
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ICONS_DIR = os.path.join(DIRECTORY, "assets", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    def log_message(self, format, *args):
        pass

server = socketserver.TCPServer(("", PORT), SilentHandler)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
time.sleep(0.3)

# Modify HTML to output the JSON data in a pre tag for easy extraction
wrapper_html = os.path.join(DIRECTORY, "scratch", "dump_icons.html")
with open(wrapper_html, "w", encoding="utf-8") as f:
    f.write(r"""<!DOCTYPE html>
<html>
<body>
<iframe id="f" src="generate_icons.html"></iframe>
<pre id="out"></pre>
<script>
window.onload = () => {
  setTimeout(() => {
    const win = document.getElementById('f').contentWindow;
    document.getElementById('out').textContent = JSON.stringify(win.iconData);
  }, 400);
};
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
    "--virtual-time-budget=2000",
    f"http://localhost:{PORT}/scratch/dump_icons.html"
]

proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
output = proc.stdout
server.shutdown()

start_tag = '<pre id="out">'
end_tag = '</pre>'

if start_tag in output and end_tag in output:
    raw_json = output.split(start_tag)[1].split(end_tag)[0].strip()
    data = json.loads(raw_json)

    files_map = {
        "icon-192.png": data["i192"],
        "icon-512.png": data["i512"],
        "icon-maskable-192.png": data["m192"],
        "icon-maskable-512.png": data["m512"]
    }

    for fname, data_url in files_map.items():
        base64_data = data_url.split(",")[1]
        file_bytes = base64.b64decode(base64_data)
        target_path = os.path.join(ICONS_DIR, fname)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        print(f"Generated {fname}: {len(file_bytes)} bytes at {target_path}")
else:
    print("Failed to extract icon data. Dump:")
    print(output[:500])
