import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")  # "Monitoring"


# 🔥 Fonction pour traduire + colorer les statuts
def format_status(value):
    if not value:
        return ""

    v = value.lower()

    if v == "error":
        return "🔴 Erreur"
    if v == "failed":
        return "🔴 Échec"
    if v == "success":
        return "🟢 Succès"
    if v == "log":
        return "🟢 Log"

    # fallback
    return value


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Lire le JSON reçu
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {e}".encode())
            return

        # URL Airtable
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Champs de base avec conversion des statuts
        fields = {
            "Workflow": body.get("Workflow", ""),
            "Module": body.get("Module", ""),

            # 🔥 Conversion automatique
            "Sensor": format_status(body.get("Sensor", "")),
            "Statut": format_status(body.get("Statut", "")),

            "Message": body.get("Message", "")
        }

        # 🔥 Date OPTIONNELLE : ajout si fournie
        date_value = body.get("Date")
        if date_value:
            fields["Date"] = date_value

        data = {"fields": fields}
        payload = json.dumps(data).encode()

        req = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())
