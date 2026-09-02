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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": "Impossibile contattare il sito"}

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Selettori ampi per intercettare i blocchi partita
        match_blocks = soup.select("main .card, .match-card, article, .row-match")
        
        risultati = []

        for block in match_blocks:
            # Cerca i nomi delle squadre
            teams = [t.text.strip() for t in block.select(".team-name, h3, h4, .name") if t.text.strip()]
            
            if len(teams) >= 2:
                # Estrae le informazioni sui giocatori o ballottaggi presenti nel blocco
                players = [p.text.strip() for p in block.select(".player, .player-name, li") if p.text.strip()]
                
                risultati.append({
                    "casa": {
                        "nome": teams[0],
                        "info": players[:len(players)//2] if players else ["Formazione in attesa"]
                    },
                    "trasferta": {
                        "nome": teams[1],
                        "info": players[len(players)//2:] if players else ["Formazione in attesa"]
                    }
                })

        # Fallback di sicurezza: se i blocchi non vengono trovati, estrae tutti i titoli di squadre disponibili
        if not risultati:
            all_teams = [t.text.strip() for t in soup.find_all(["h2", "h3", "strong"]) if len(t.text.strip()) > 2]
            # Filtra e accoppia i nomi rilevati
            for i in range(0, len(all_teams) - 1, 2):
                risultati.append({
                    "casa": {"nome": all_teams[i], "info": ["Scheda in aggiornamento"]},
                    "trasferta": {"nome": all_teams[i+1], "info": ["Scheda in aggiornamento"]}
                })

        return {"status": "success", "matches": risultati[:10]}

    except Exception as e:
        return {"status": "error", "message": str(e)}
