import subprocess
import os

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
test_url = "http://localhost:8095/index.html"

# Run Chrome with remote debugging or dump layout via JS in console
js_script = """
const c = document.querySelector('.app-container');
const b = document.body;
const hero = document.querySelector('.streak-hero');
console.log('BODY:', b.offsetWidth, b.scrollWidth, window.innerWidth);
console.log('CONTAINER:', c.offsetWidth, c.getBoundingClientRect().left, c.getBoundingClientRect().right);
console.log('HERO:', hero.offsetWidth, hero.getBoundingClientRect().left);
"""
print("Running diagnostic...")
