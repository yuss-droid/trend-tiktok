import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 8080
folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(folder)

Handler = http.server.SimpleHTTPRequestHandler

def open_browser():
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

print("=" * 50)
print(f"🚀 SERVER BERJALAN: http://localhost:{PORT}")
print("Membuka browser otomatis...")
print("Tekan Ctrl+C di terminal ini untuk mematikan server.")
print("=" * 50)

threading.Thread(target=open_browser).start()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dimatikan.")
