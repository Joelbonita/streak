import subprocess
import time
import http.server
import socketserver
import threading
import os

PORT = 8092
DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
test_url = f"http://localhost:{PORT}/scratch/e2e_test.html"

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--dump-dom",
    "--virtual-time-budget=2000",
    test_url
]

try:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    html_output = proc.stdout
    start_tag = '<div id="results">'
    end_tag = '</div>'
    if start_tag in html_output and end_tag in html_output:
        content = html_output.split(start_tag)[1].split(end_tag)[0]
        # print line by line
        for line in content.split('<br>'):
            print(line.strip())
    else:
        print("DOM dump:")
        print(html_output[:600])
except Exception as e:
    print(f"Error running test: {e}")
