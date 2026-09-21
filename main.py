import time
import os
import cloudscraper
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- KONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1551491729582985257/wAgRZuueB2E1A-ki-s4RV60MJuINEnvp6UiwUIivNypMLSxhjlcNIeNO8aMT0Dn_Vxa_"
NINEGAG_USER = "bernd_hoecke"
CHECK_INTERVAL = 300
# ---------------------

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"9GAG Bot laeuft!")

def run_webserver():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleServer)
    server.serve_forever()

def tracker_loop():
    scraper = cloudscraper.create_scraper()
    API_URL = f"https://9gag.com{NINEGAG_USER}"
    bekannte_gags = set()
    erststart = True
    print(f"[*] 9GAG-Tracker gestartet...")
    while True:
        try:
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            response = scraper.get(API_URL, headers=headers)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("posts", [])
                if posts:
                    neuester_post = posts[0]
                    post_id = neuester_post.get("id")
                    post_title = neuester_post.get("title", "Kein Titel")
                    post_url = neuester_post.get("url")
                    if erststart:
                        bekannte_gags.add(post_id)
                        erststart = False
                    elif post_id not in bekannte_gags:
                        bekannte_gags.add(post_id)
                        payload = {
                            "username": "9GAG Bot",
                            "avatar_url": "https://9gag.com",
                            "embeds": [{
                                "title": "🔔 Neuer Post von bernd_hoecke!",
                                "description": post_title,
                                "url": post_url,
                                "color": 0
                            }]
                        }
                        requests.post(DISCORD_WEBHOOK_URL, json=payload)
            time.sleep(CHECK_INTERVAL)
        except Exception:
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_webserver, daemon=True).start()
    tracker_loop()
  
