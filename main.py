import time
import os
import cloudscraper
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- KONFIGURATION ---
# Deine eingetragene Discord Webhook-URL
DISCORD_WEBHOOK_URL = "https://discord.com_"

# GRUPPE 1: Positives Framing (Grüne Nachricht)
PRO_USERS = [
    "bernd_hoecke"
]

# GRUPPE 2: Negatives Framing (Rote Nachricht)
CONTRA_USERS = [
    "rehpfosten",
    "mr_hardwood",
    "admiral_bernd"
]

# Prüf-Intervall: Alle 5 Minuten (300 Sekunden)
CHECK_INTERVAL = 300
# ---------------------

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"9GAG Framed Bot laeuft!")

def run_webserver():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleServer)
    server.serve_forever()

def tracker_loop():
    scraper = cloudscraper.create_scraper()
    bekannte_gags = set()
    erststart = True
    
    alle_nutzer = PRO_USERS + CONTRA_USERS
    print(f"[*] Tracker gestartet... Überwache {len(alle_nutzer)} Nutzer.")
    
    while True:
        for user in alle_nutzer:
            try:
                api_url = f"https://9gag.com{user}"
                headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
                response = scraper.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("posts", [])
                    
                    if posts:
                        neuester_post = posts[0]
                        post_id = neuester_post.get("id")
                        post_title = neuester_post.get("title", "Kein Titel")
                        post_url = neuester_post.get("url")
                        
                        speicher_key = f"{user}_{post_id}"
                        
                        if erststart:
                            bekannte_gags.add(speicher_key)
                        elif speicher_key not in bekannte_gags:
                            bekannte_gags.add(speicher_key)
                            
                            embed_title = f"🔔 Neuer Post von {user}"
                            embed_color = 8421504
                            
                            # Individuelles Framing je nach Gruppe
                            if user in PRO_USERS:
                                embed_title = f"💚 Großartige Neuigkeiten! {user} hat etwas Neues gepostet!"
                                embed_color = 3066993  # Grün
                            elif user in CONTRA_USERS:
                                embed_title = f"⚠️ Achtung: {user} hat schon wieder Müll hochgeladen!"
                                embed_color = 15158332  # Rot
                            
                            payload = {
                                "username": "9GAG News Radar",
                                "avatar_url": "https://9gag.com",
                                "embeds": [{
                                    "title": embed_title,
                                    "description": f"**Titel:** {post_title}\n\n[Hier geht's zum Beitrag]({post_url})",
                                    "url": post_url,
                                    "color": embed_color
                                }]
                            }
                            requests.post(DISCORD_WEBHOOK_URL, json=payload)
                            print(f"[+] Post von {user} verarbeitet und gesendet.")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"[-] Fehler bei {user}: {e}")
                
        if erststart:
            print("[i] Aktuelle Posts eingelesen. Bot wartet auf neue Uploads...")
            erststart = False
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=run_webserver, daemon=True).start()
    tracker_loop()
                
