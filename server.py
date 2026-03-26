#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║   DOCOL WELLNESS — Servidor de Coleta de Insights    ║
║   Portfólio BE · ExpoRevestir 2026                   ║
╚══════════════════════════════════════════════════════╝

USO:
  python server.py

  O servidor inicia em http://0.0.0.0:8080
  Compartilhe o IP da sua máquina com os participantes.
  
  Para descobrir seu IP:
    - macOS/Linux: ifconfig | grep "inet "
    - Windows: ipconfig

  Participantes acessam: http://SEU_IP:8080
  Facilitador acessa:    http://SEU_IP:8080/#facilitador
"""

import json
import os
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime

# ─── In-memory data store ───
DATA = {
    "participants": [],
    "notes": {}
}
DATA_LOCK = threading.Lock()
BACKUP_FILE = "docol_wellness_backup.json"
PORT = int(os.environ.get("PORT", 8080))

# Load from backup if exists
if os.path.exists(BACKUP_FILE):
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            DATA = json.load(f)
        print(f"  ✓ Backup carregado: {len(DATA.get('participants',[]))} participantes, "
              f"{sum(len(v) for v in DATA.get('notes',{}).values())} cards")
    except Exception as e:
        print(f"  ⚠ Erro ao carregar backup: {e}")

def save_backup():
    """Save data to JSON file"""
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(DATA, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ⚠ Erro ao salvar backup: {e}")

# Auto-backup every 30 seconds
def auto_backup():
    while True:
        time.sleep(30)
        with DATA_LOCK:
            save_backup()

backup_thread = threading.Thread(target=auto_backup, daemon=True)
backup_thread.start()


class WellnessHandler(SimpleHTTPRequestHandler):
    """Custom handler for API + static file serving"""
    
    def log_message(self, format, *args):
        """Custom log format"""
        if "/api/" in str(args[0]):
            method = str(args[0]).split(" ")[0]
            path = str(args[0]).split(" ")[1] if len(str(args[0]).split(" ")) > 1 else ""
            status = args[1] if len(args) > 1 else ""
            print(f"  {method} {path} → {status}")
    
    def send_json(self, data, status=200):
        """Helper to send JSON responses"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def read_body(self):
        """Read and parse JSON body"""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body) if body else {}
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/api/data":
            with DATA_LOCK:
                self.send_json(DATA)
        
        elif path == "/api/stats":
            with DATA_LOCK:
                total_notes = sum(len(v) for v in DATA.get("notes", {}).values())
                self.send_json({
                    "participants": len(DATA.get("participants", [])),
                    "total_notes": total_notes,
                    "by_product": {k: len(v) for k, v in DATA.get("notes", {}).items()}
                })
        
        elif path == "/api/export":
            with DATA_LOCK:
                export = {
                    "exportedAt": datetime.now().isoformat(),
                    **DATA
                }
                self.send_json(export)
        
        else:
            # Serve index.html directly with strong cache headers
            if path == "/" or path == "" or path == "/index.html":
                self.serve_html()
            else:
                super().do_GET()
    
    def serve_html(self):
        """Serve index.html with cache headers that prevent reload"""
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        try:
            with open(html_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "max-age=3600, must-revalidate")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "index.html not found")
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == "/api/participants":
            body = self.read_body()
            if not body.get("name") or not body.get("team"):
                self.send_json({"error": "name and team required"}, 400)
                return
            participant = {
                "id": f"p_{int(time.time()*1000)}_{os.urandom(3).hex()}",
                "name": body["name"],
                "team": body["team"],
                "joinedAt": datetime.now().isoformat()
            }
            with DATA_LOCK:
                DATA["participants"].append(participant)
                save_backup()
            self.send_json(participant, 201)
        
        elif path == "/api/notes":
            body = self.read_body()
            if not body.get("productId") or not body.get("text"):
                self.send_json({"error": "productId and text required"}, 400)
                return
            note = {
                "id": f"n_{int(time.time()*1000)}_{os.urandom(3).hex()}",
                "productId": body["productId"],
                "text": body["text"],
                "category": body.get("category", "geral"),
                "author": body.get("author", "Anônimo"),
                "team": body.get("team", ""),
                "colorIdx": body.get("colorIdx", 0),
                "createdAt": datetime.now().isoformat()
            }
            pid = note["productId"]
            with DATA_LOCK:
                if pid not in DATA["notes"]:
                    DATA["notes"][pid] = []
                DATA["notes"][pid].append(note)
                save_backup()
            self.send_json(note, 201)
        
        elif path == "/api/reset":
            with DATA_LOCK:
                DATA["participants"] = []
                DATA["notes"] = {}
                save_backup()
            self.send_json({"status": "reset complete"})
        
        else:
            self.send_json({"error": "not found"}, 404)
    
    def do_DELETE(self):
        path = urlparse(self.path).path
        
        if path.startswith("/api/notes/"):
            note_id = path.split("/")[-1]
            with DATA_LOCK:
                for pid in DATA["notes"]:
                    DATA["notes"][pid] = [n for n in DATA["notes"][pid] if n["id"] != note_id]
                save_backup()
            self.send_json({"status": "deleted"})
        else:
            self.send_json({"error": "not found"}, 404)


def get_local_ip():
    """Try to find the local network IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


if __name__ == "__main__":
    ip = get_local_ip()
    
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║     DOCOL WELLNESS — Coleta de Insights      ║")
    print("  ║     Portfólio BE · ExpoRevestir 2026         ║")
    print("  ╠══════════════════════════════════════════════╣")
    print(f"  ║                                              ║")
    print(f"  ║  Participantes: http://{ip}:{PORT}        ║")
    print(f"  ║  Facilitador:   http://{ip}:{PORT}/#facilitador ║")
    print(f"  ║                                              ║")
    print(f"  ║  Backup: {BACKUP_FILE}          ║")
    print("  ║  Ctrl+C para encerrar                        ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()
    
    server = HTTPServer(("0.0.0.0", PORT), WellnessHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Encerrando servidor...")
        with DATA_LOCK:
            save_backup()
        print(f"  ✓ Backup final salvo em {BACKUP_FILE}")
        print("  Até logo! 👋")
        server.server_close()
