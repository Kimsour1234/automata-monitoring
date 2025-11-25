import os
import json
import requests
from http.server import BaseHTTPRequestHandler

# ----------------------------
# ENV VARIABLES (Vercel)
# ----------------------------
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Lire le JSON envoyé par Make
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {e}".encode())
            return

        # ----------------------------
        # Construction URL Airtable
        # ----------------------------
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        # ----------------------------
        # Mapping EXACT des colonnes
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
                "Date": body.get("Date", "")
            }
        }

        # ----------------------------
        # Envoi vers Airtable
        # ----------------------------
        try:
            r = requests.post(url, json=data, headers=headers)

            if r.status_code in (200, 201):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Airtable error: {r.text}".encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Request failed: {e}".encode())
