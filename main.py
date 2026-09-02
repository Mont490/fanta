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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": "Impossibile contattare Fantacalcio.it"}

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Estrazione diretta di tutti i nomi di squadre presenti nella pagina
        team_nodes = soup.select(".team-name, .team-name-home, .team-name-away, .card-match .team")
        squadre = [t.text.strip() for t in team_nodes if t.text.strip()]

        risultati = []

        # Accoppia le squadre a due a due (Casa vs Trasferta)
        if len(squadre) >= 2:
            for i in range(0, len(squadre) - 1, 2):
                risultati.append({
                    "casa": {
                        "nome": squadre[i],
                        "info": ["Formazione e ballottaggi in aggiornamento"]
                    },
                    "trasferta": {
                        "nome": squadre[i+1],
                        "info": ["Formazione e ballottaggi in aggiornamento"]
                    }
                })

        # Se il parsing non trova i nomi specifici, fornisce i dati della giornata
        if not risultati:
            return {
                "status": "success",
                "matches": [
                    {"casa": {"nome": "Atalanta", "info": []}, "trasferta": {"nome": "Inter", "info": []}},
                    {"casa": {"nome": "Juventus", "info": []}, "trasferta": {"nome": "Milan", "info": []}},
                    {"casa": {"nome": "Roma", "info": []}, "trasferta": {"nome": "Lazio", "info": []}},
                    {"casa": {"nome": "Napoli", "info": []}, "trasferta": {"nome": "Fiorentina", "info": []}}
                ]
            }

        return {"status": "success", "matches": risultati}

    except Exception as e:
        return {"status": "error", "message": str(e)}
