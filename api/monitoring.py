import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")  # "Monitoring_3"


# 🔥 Fonction pour traduire + colorer le statut
def format_status(value):
    if not value:
        return ""

    v = value.lower()

    if v == "success":
        return "🟢 Success"
    if v == "error":
        return "🔴 Error"
    if v == "failed":
        return "🔴 Failed"
    if v == "log":
        return "🟢 Log"

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

        # Champs EXACTS adaptés à ta table Monitoring_3
        fields = {
            "Workflow": body.get("Workflow", ""),
            "Module": body.get("Module", ""),
            "Type": body.get("Type", ""),                   # success / error
            "Status": format_status(body.get("Status", "")),# 🟢 Success / 🔴 Error
            "Message": body.get("Message", "")
        }

        data = {"fields": fields}
        payload = json.dumps(data).encode()

        req = urllib.request.Request(
            url, data=payload, headers=headers, method="POST"
        )

        try:
            urllib.request.urlopen(req)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())
