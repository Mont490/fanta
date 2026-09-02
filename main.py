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
        
        # Struttura contenitori partite su Fantacalcio.it
        match_cards = soup.find_all("li", class_="match-item") or soup.find_all("div", class_="match")

        risultati = []

        for card in match_cards:
            # Squadre
            home_team = card.find("span", class_="team-name-home") or card.select_one(".home .team-name")
            away_team = card.find("span", class_="team-name-away") or card.select_one(".away .team-name")

            if not home_team or not away_team:
                continue

            # Giocatori titolari / Formazioni
            home_players = [p.text.strip() for p in card.select(".home .player-name, .home .player")]
            away_players = [p.text.strip() for p in card.select(".away .player-name, .away .player")]

            # Ballottaggi
            ballottaggi = [b.text.strip() for b in card.select(".ballot-item, .ballottaggio")]

            risultati.append({
                "casa": {
                    "nome": home_team.text.strip(),
                    "titolari": home_players if home_players else ["In attesa di inserimento"]
                },
                "trasferta": {
                    "nome": away_team.text.strip(),
                    "titolari": away_players if away_players else ["In attesa di inserimento"]
                },
                "ballottaggi": ballottaggi
            })

        if not risultati:
            # Se la pagina cambia struttura improvvisamente, estraiamo i nomi dei club generici
            teams = [t.text.strip() for t in soup.select(".team-name")]
            for i in range(0, len(teams) - 1, 2):
                risultati.append({
                    "casa": {"nome": teams[i], "titolari": ["Vedi scheda completa su Fantacalcio"]},
                    "trasferta": {"nome": teams[i+1], "titolari": ["Vedi scheda completa su Fantacalcio"]},
                    "ballottaggi": []
                })

        return {"status": "success", "matches": risultati}

    except Exception as e:
        return {"status": "error", "message": str(e)}
