from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.support_ticket import router as router_support_ticket
import os

app = FastAPI(title="SmartHelp API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Créer le dossier temporaire s'il n'existe pas
os.makedirs("temp_files", exist_ok=True)

app.include_router(router_support_ticket)

@app.get("/")
def accueil():
    return {"message": "SmartHelp API - Bienvenue"}



