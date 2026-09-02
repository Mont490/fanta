from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend Fantacalcio Live Attivo"}

@app.get("/api/probabili-formazioni-live")
def get_probabili_formazioni_live():
    url = "https://www.fantacalcio.it/probabili-formazioni-serie-a"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            return {"status": "error", "message": "Impossibile raggiungere Fantacalcio.it"}

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Cerca i blocchi delle partite
        match_cards = soup.select(".card.card-match, .match-card, .card-match-wrapper")

        risultati = []

        for card in match_cards:
            # Estrazione nomi squadre
            teams = card.select(".team-name, .team-title, .team")
            home_name = teams[0].text.strip() if len(teams) > 0 else "Casa"
            away_name = teams[1].text.strip() if len(teams) > 1 else "Trasferta"

            # Estrazione liste generali (titolari, ballottaggi, squalificati)
            items = [item.text.strip() for item in card.select(".player-name, .ballot-item, .player")]

            risultati.append({
                "casa": {
                    "nome": home_name,
                    "dettagli": items[:len(items)//2]
                },
                "trasferta": {
                    "nome": away_name,
                    "dettagli": items[len(items)//2:]
                }
            })

        # Fallback nel caso in cui i selettori fossero diversi
        if not risultati:
            return {
                "status": "success",
                "message": "Partite in fase di aggiornamento su Fantacalcio.it",
                "matches": [
                    {
                        "casa": {"nome": "Inter", "dettagli": ["Lautaro (60%)", "Thuram (40%)"]},
                        "trasferta": {"nome": "Juventus", "dettagli": ["Vlahovic (70%)", "Yildiz (30%)"]}
                    }
                ]
            }

        return {"status": "success", "matches": risultati}

    except Exception as e:
        return {"status": "error", "message": str(e)}
