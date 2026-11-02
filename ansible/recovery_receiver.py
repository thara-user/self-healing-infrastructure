
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).with_name("recovery_receiver.log")

PLAYBOOK = (
    "/mnt/c/Users/ittth/self-healing-infrastructure/"
    "ansible/recovery.yml"
)


def log(message):
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp} {message}"
    print(line, flush=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


class AlertHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        log(f"Received POST {self.path}")

        if self.path != "/alert":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            log("Invalid JSON received")
            self.send_error(400, "Invalid JSON")
            return

        recovery_attempted = False
        recovery_succeeded = False

        for alert in payload.get("alerts", []):
            labels = alert.get("labels", {})
            status = alert.get("status")

            alert_name = labels.get("alertname")

            log(
                f"Alert received: name={alert_name}, "
                f"status={status}"
            )

            if alert_name == "NginxDown" and status == "firing":
                recovery_attempted = True

                try:
                    result = subprocess.run(
                        [
                            "wsl.exe",
                            "-d",
                            "Ubuntu",
                            "--",
                            "ansible-playbook",
                            PLAYBOOK
                        ],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    log(f"Ansible exit code: {result.returncode}")

                    if result.stdout.strip():
                        log(f"Ansible output: {result.stdout.strip()}")

                    if result.stderr.strip():
                        log(
                            "Ansible errors/warnings: "
                            f"{result.stderr.strip()}"
                        )

                    recovery_succeeded = result.returncode == 0

                except Exception as error:
                    log(f"Recovery exception: {error}")

                break

        response = json.dumps({
            "received": True,
            "recovery_attempted": recovery_attempted,
            "recovery_succeeded": recovery_succeeded
        }).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        log(format % args)


if __name__ == "__main__":
    log("Recovery receiver listening on port 5001")
    HTTPServer(("0.0.0.0", 5001), AlertHandler).serve_forever()
