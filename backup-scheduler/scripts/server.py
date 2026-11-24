#!/usr/bin/env python3
"""
Microservicio HTTP interno del Backup-Scheduler.
Permite a la API central disparar respaldos manuales y consultar la lista de artefactos en SILO S3.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json
import os

class BackupHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path in ('/health', '/'):
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "backup-scheduler-agent",
                "cron": "0 2 * * 0"
            }).encode('utf-8'))
        elif self.path == '/list':
            try:
                cmd = ["aws", "--endpoint-url", "http://minio:9000", "s3", "ls", "s3://respaldosbd/", "--recursive"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                files = []
                for line in res.stdout.strip().splitlines():
                    parts = line.split(maxsplit=3)
                    if len(parts) == 4:
                        date_str = f"{parts[0]} {parts[1]}"
                        try:
                            size = int(parts[2])
                        except ValueError:
                            size = 0
                        key = parts[3]
                        engine = "SQL Server 2025" if "sqlserver" in key.lower() else "MongoDB 8"
                        files.append({
                            "key": key,
                            "filename": os.path.basename(key),
                            "engine": engine,
                            "size_bytes": size,
                            "size_human": self._format_size(size),
                            "timestamp": date_str
                        })
                # Ordenar por fecha descendente
                files.reverse()
                self._set_headers(200)
                self.wfile.write(json.dumps({"files": files, "count": len(files)}).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/run':
            try:
                res = subprocess.run(
                    ["/bin/sh", "/scripts/backup-semanal.sh"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                output = res.stdout
                if res.stderr:
                    output += "\n" + res.stderr
                success = (res.returncode == 0)
                self._set_headers(200 if success else 500)
                self.wfile.write(json.dumps({
                    "success": success,
                    "returncode": res.returncode,
                    "output": output
                }).encode('utf-8'))
            except subprocess.TimeoutExpired:
                self._set_headers(504)
                self.wfile.write(json.dumps({"success": False, "error": "Timeout al ejecutar el respaldo"}).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode('utf-8'))

    def _format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

    def log_message(self, format, *args):
        # Silenciar logs para no saturar salida estándar
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8088), BackupHandler)
    server.serve_forever()
