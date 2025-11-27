import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {e}".encode())
            return

        # -------------------------------
        # Gestion de la date universelle
        # -------------------------------
        raw_date = body.get("Date", "")

        try:
            # si Make envoie une date ISO
            d = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            final_date = d.strftime("%Y-%m-%d %H:%M:%S")
        except:
            # fallback : date actuelle
            final_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "fields": {
                "Workflow": body.get("Workflow", ""),
                "Module": body.get("Module", ""),
                "Sensor": body.get("Sensor", ""),
                "Statut": body.get("Statut", ""),
                "Message": body.get("Message", ""),
                "Date": final_date
            }
        }

        payload = json.dumps(data).encode()

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())
