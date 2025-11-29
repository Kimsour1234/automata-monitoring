import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

# ✔️ EXACT : c'est la variable Vercel qui contient "Monitoring 2"
AIRTABLE_TABLE_MONITORING_IA = os.environ.get("AIRTABLE_TABLE_MONITORING_IA")


def format_status(value):
    if not value:
        return ""

    v = value.lower()

    # Sensor
    if v == "log":
        return "🟢 Log"
    if v == "erreur":
        return "🔴 Erreur"

    # Statut
    if v == "succès":
        return "🟢 Succès"
    if v == "échec":
        return "🔴 Échec"

    return value


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

        # 🔥 La table IA = "Monitoring 2"
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_MONITORING_IA}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        fields = {
            # Logs de base
            "Workflow": body.get("Workflow", ""),
            "Module": body.get("Module", ""),
            "Sensor": format_status(body.get("Sensor", "")),
            "Statut": format_status(body.get("Statut", "")),
            "Message": body.get("Message", ""),

            # Champs IA
            "Résumé global": body.get("ResumeGlobal", ""),
            "Tendances détectées": body.get("Tendances", ""),
            "Modules à risque": body.get("ModulesRisque", ""),
            "Recommandations": body.get("Recommandations", ""),
            "Top 3 priorités": body.get("Priorites", ""),

            "Période analysée": body.get("Periode", ""),
            "Total logs": body.get("TotalLogs", None),
            "Total erreurs": body.get("TotalErreurs", None)
        }

        payload = json.dumps({"fields": fields}).encode()

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
