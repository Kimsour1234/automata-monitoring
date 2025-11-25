import os
import json
import urllib.request
from urllib.error import HTTPError
from http.server import BaseHTTPRequestHandler

# ----------------------------
# VARIABLES ENV
# ----------------------------
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Lire JSON reçu
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # ----------------------------
        # Gestion date (Airtable refuse les dates vides)
        # ----------------------------
        date_value = body.get("Date")
        if not date_value:
            date_value = "2025-01-01"  # valeur par défaut valide

        # ----------------------------
        # Construction payload Airtable
        # ----------------------------
        data = {
            "fields": {
                "Monitoring": body.get("Monitoring", ""),
                "Automata": body.get("Automata", ""),
                "Client": body.get("Client", ""),
                "Type": body.get("Type", ""),
                "Statut": body.get("Statut", ""),
                "Module": body.get("Module", ""),
                "Message": body.get("Message", ""),
                "Date": date_value
            }
        }

        payload = json.dumps(data).encode()

        # ----------------------------
        # Requête Airtable
        # ----------------------------
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            urllib.request.urlopen(req)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except HTTPError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e.code}".encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())
