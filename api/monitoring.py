import os
import json
import urllib.request
from urllib.error import HTTPError
from http.server import BaseHTTPRequestHandler

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")

print("DEBUG - AIRTABLE_API_KEY:", AIRTABLE_API_KEY)
print("DEBUG - AIRTABLE_BASE_ID:", AIRTABLE_BASE_ID)
print("DEBUG - AIRTABLE_TABLE_NAME:", AIRTABLE_TABLE_NAME)


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

        print("DEBUG - JSON reçu:", body)

        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        print("DEBUG - URL:", url)

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

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

        print("DEBUG - Data envoyée:", data)

        payload = json.dumps(data).encode()
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            response = urllib.request.urlopen(req)
            result = response.read().decode()
            print("DEBUG - Airtable Response:", result)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except HTTPError as e:
            err_body = e.read().decode()
            print("DEBUG - Airtable HTTPError code:", e.code)
            print("DEBUG - Airtable ERROR BODY:", err_body)

            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e.code} {err_body}".encode())

        except Exception as e:
            print("DEBUG - Airtable OTHER ERROR:", e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())
