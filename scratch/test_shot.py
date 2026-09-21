import subprocess
import os

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ARTIFACT_DIR = r"C:\Users\WINDOWS 10\.gemini\antigravity\brain\0b3ccf88-423c-42b1-bbcc-6bb39fe2dc1b"

# Test taking screenshot with window-size 800,900
out_img = os.path.join(ARTIFACT_DIR, "screenshot_mobile_centered.png")
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--window-size=600,900",
    f"--screenshot={out_img}",
    "http://localhost:8099/index.html"
]
subprocess.run(cmd, capture_output=True, text=True, timeout=10)
print("Centered screenshot generated:", os.path.exists(out_img))
