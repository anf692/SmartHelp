from fastapi import FastAPI
from routes.support_ticket import router as router_support_ticket
import os

app = FastAPI(title="SmartHelp API")

# Créer le dossier temporaire s'il n'existe pas
os.makedirs("temp_files", exist_ok=True)

app.include_router(router_support_ticket)

@app.get("/")
def accueil():
    return {"message": "SmartHelp API - Bienvenue"}



