from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Berlusca Dortmund API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Giocatore(BaseModel):
    nome: str
    ruolo: str
    squadra: str
    forma: float
    titolare_prob: float
    avversario_facilita: float
    bonus_attesi: float
    casa: bool
    media_voto: float = 6.00
    fantamedia: float = 6.00
    gol: int = 0
    assist: int = 0

    def calcola_is(self) -> float:
        casa_val = 100.0 if self.casa else 50.0
        score = (
            (self.avversario_facilita * 0.30)
            + (self.titolare_prob * 0.25)
            + (self.forma * 0.20)
            + (self.bonus_attesi * 0.15)
            + (casa_val * 0.10)
        )
        return round(score, 1)

ROSA_DB = [
    # Portieri
    Giocatore(nome="De Gea", ruolo="P", squadra="Fiorentina", forma=80, titolare_prob=100, avversario_facilita=70, bonus_attesi=20, casa=True, media_voto=6.45, fantamedia=5.85, gol=0, assist=1),
    Giocatore(nome="Stankovic", ruolo="P", squadra="Venezia", forma=60, titolare_prob=100, avversario_facilita=40, bonus_attesi=10, casa=False, media_voto=6.10, fantamedia=4.90, gol=0, assist=0),
    Giocatore(nome="Muric", ruolo="P", squadra="Sassuolo", forma=50, titolare_prob=0, avversario_facilita=50, bonus_attesi=0, casa=False, media_voto=5.90, fantamedia=4.50, gol=0, assist=0),
    # Difensori
    Giocatore(nome="Dimarco", ruolo="D", squadra="Inter", forma=85, titolare_prob=95, avversario_facilita=80, bonus_attesi=85, casa=True, media_voto=6.35, fantamedia=7.20, gol=4, assist=6),
    Giocatore(nome="Carlos Augusto", ruolo="D", squadra="Inter", forma=70, titolare_prob=60, avversario_facilita=80, bonus_attesi=50, casa=True, media_voto=6.15, fantamedia=6.40, gol=1, assist=2),
    Giocatore(nome="Kolasinac", ruolo="D", squadra="Atalanta", forma=75, titolare_prob=90, avversario_facilita=70, bonus_attesi=40, casa=True, media_voto=6.20, fantamedia=6.30, gol=1, assist=1),
    Giocatore(nome="Marusic", ruolo="D", squadra="Lazio", forma=65, titolare_prob=80, avversario_facilita=60, bonus_attesi=30, casa=False, media_voto=5.95, fantamedia=6.05, gol=0, assist=1),
    Giocatore(nome="Jimenez", ruolo="D", squadra="Milan", forma=60, titolare_prob=50, avversario_facilita=70, bonus_attesi=30, casa=True, media_voto=5.85, fantamedia=5.90, gol=0, assist=0),
    Giocatore(nome="Obert", ruolo="D", squadra="Cagliari", forma=55, titolare_prob=70, avversario_facilita=50, bonus_attesi=10, casa=False, media_voto=5.80, fantamedia=5.75, gol=0, assist=0),
    Giocatore(nome="Marcandalli", ruolo="D", squadra="Genoa", forma=50, titolare_prob=30, avversario_facilita=40, bonus_attesi=0, casa=False, media_voto=5.70, fantamedia=5.65, gol=0, assist=0),
    # Centrocampisti
    Giocatore(nome="De Bruyne", ruolo="C", squadra="Fantacalcio", forma=80, titolare_prob=90, avversario_facilita=75, bonus_attesi=80, casa=True, media_voto=6.50, fantamedia=7.80, gol=5, assist=7),
    Giocatore(nome="Fazzini", ruolo="C", squadra="Empoli", forma=70, titolare_prob=85, avversario_facilita=60, bonus_attesi=60, casa=True, media_voto=6.10, fantamedia=6.50, gol=2, assist=1),
    Giocatore(nome="Lobotka", ruolo="C", squadra="Napoli", forma=75, titolare_prob=100, avversario_facilita=80, bonus_attesi=20, casa=True, media_voto=6.25, fantamedia=6.30, gol=0, assist=2),
    Giocatore(nome="Diouf", ruolo="C", squadra="Verona", forma=60, titolare_prob=70, avversario_facilita=50, bonus_attesi=30, casa=False, media_voto=5.90, fantamedia=6.00, gol=1, assist=0),
    Giocatore(nome="Calò", ruolo="C", squadra="Cesena", forma=55, titolare_prob=60, avversario_facilita=50, bonus_attesi=20, casa=False, media_voto=6.00, fantamedia=6.10, gol=0, assist=2),
    # Attaccanti
    Giocatore(nome="Dovbyk", ruolo="A", squadra="Roma", forma=85, titolare_prob=95, avversario_facilita=80, bonus_attesi=90, casa=True, media_voto=6.30, fantamedia=7.90, gol=11, assist=3),
    Giocatore(nome="Hojlund", ruolo="A", squadra="Atalanta", forma=80, titolare_prob=90, avversario_facilita=75, bonus_attesi=85, casa=True, media_voto=6.40, fantamedia=7.75, gol=9, assist=2),
    Giocatore(nome="Castro", ruolo="A", squadra="Bologna", forma=75, titolare_prob=80, avversario_facilita=70, bonus_attesi=70, casa=False, media_voto=6.20, fantamedia=7.10, gol=6, assist=4),
    Giocatore(nome="Lucca", ruolo="A", squadra="Udinese", forma=70, titolare_prob=85, avversario_facilita=65, bonus_attesi=75, casa=True, media_voto=6.15, fantamedia=7.30, gol=8, assist=1),
    Giocatore(nome="Pio Esposito", ruolo="A", squadra="Spezia", forma=65, titolare_prob=70, avversario_facilita=60, bonus_attesi=60, casa=False, media_voto=6.05, fantamedia=6.70, gol=4, assist=1),
    Giocatore(nome="Milik", ruolo="A", squadra="Juventus", forma=40, titolare_prob=0, avversario_facilita=50, bonus_attesi=30, casa=False, media_voto=5.50, fantamedia=5.50, gol=0, assist=0),
]

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/api/consigli")
def get_consigli(ruolo: Optional[str] = None):
    risultato = []
    for g in ROSA_DB:
        if not ruolo or ruolo.upper() == "ALL" or g.ruolo == ruolo.upper():
            risultato.append({
                "nome": g.nome,
                "ruolo": g.ruolo,
                "squadra": g.squadra,
                "is_score": g.calcola_is(),
                "media_voto": g.media_voto,
                "fantamedia": g.fantamedia,
                "gol": g.gol,
                "assist": g.assist,
                "spiegazione": f"{'Casa' if g.casa else 'Trasferta'} | Titolarità: {g.titolare_prob}% | Forma: {g.forma}/100"
            })
    return sorted(risultato, key=lambda x: x["is_score"], reverse=True)

@app.get("/api/formazione-ottimale")
def get_formazione_ottimale():
    portieri = sorted([g for g in ROSA_DB if g.ruolo == "P"], key=lambda x: x.calcola_is(), reverse=True)
    difensori = sorted([g for g in ROSA_DB if g.ruolo == "D"], key=lambda x: x.calcola_is(), reverse=True)
    centrocampisti = sorted([g for g in ROSA_DB if g.ruolo == "C"], key=lambda x: x.calcola_is(), reverse=True)
    attaccanti = sorted([g for g in ROSA_DB if g.ruolo == "A"], key=lambda x: x.calcola_is(), reverse=True)

    moduli = [(4, 3, 3), (4, 4, 2), (5, 3, 2), (5, 4, 1)]
    best_score = -1
    best_modulo = "4-3-3"
    best_11 = []

    for num_d, num_c, num_a in moduli:
        if len(difensori) >= num_d and len(centrocampisti) >= num_c and len(attaccanti) >= num_a:
            tit_d, tit_c, tit_a = difensori[:num_d], centrocampisti[:num_c], attaccanti[:num_a]
            score = portieri[0].calcola_is() + sum(d.calcola_is() for d in tit_d) + sum(c.calcola_is() for c in tit_c) + sum(a.calcola_is() for a in tit_a)
            
            if score > best_score:
                best_score = score
                best_modulo = f"{num_d}-{num_c}-{num_a}"
                best_11 = [portieri[0]] + tit_d + tit_c + tit_a

    titolari_nomi = set(g.nome for g in best_11)
    panchina = [g for g in ROSA_DB if g.nome not in titolari_nomi]

    return {
        "modulo": best_modulo,
        "punteggio_totale": round(best_score, 1),
        "titolari": [{"nome": g.nome, "ruolo": g.ruolo, "squadra": g.squadra, "is": g.calcola_is()} for g in best_11],
        "panchina": [{"nome": g.nome, "ruolo": g.ruolo, "squadra": g.squadra, "is": g.calcola_is()} for g in sorted(panchina, key=lambda x: (x.ruolo, -x.calcola_is()))]
    }
