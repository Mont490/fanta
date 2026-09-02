from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Permette al frontend su GitHub Pages di fare richieste a questo backend
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": "Impossibile contattare Fantacalcio.it"}

        soup = BeautifulSoup(response.text, "html.parser")
        match_cards = soup.find_all("div", class_="card-match")

        risultati = []
        for card in match_cards:
            home_team = card.find("span", class_="team-name-home")
            away_team = card.find("span", class_="team-name-away")

            if home_team and away_team:
                risultati.append({
                    "casa": {
                        "nome": home_team.text.strip(),
                        "ballottaggi": [b.text.strip() for b in card.select(".home-ballot .ballot-item")],
                        "squalificati": [s.text.strip() for s in card.select(".home-squalificati .player-name")],
                        "infortunati": [i.text.strip() for i in card.select(".home-infortunati .player-name")]
                    },
                    "trasferta": {
                        "nome": away_team.text.strip(),
                        "ballottaggi": [b.text.strip() for b in card.select(".away-ballot .ballot-item")],
                        "squalificati": [s.text.strip() for s in card.select(".away-squalificati .player-name")],
                        "infortunati": [i.text.strip() for i in card.select(".away-infortunati .player-name")]
                    }
                })

        return {"status": "success", "matches": risultati}

    except Exception as e:
        return {"status": "error", "message": str(e)}
