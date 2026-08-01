# services/vision_service.py

from functools import lru_cache
from transformers import pipeline
from PIL import Image
import io

@lru_cache()
def charger_modele_vision():
    """
    Charge le modèle de classification d'image une seule fois en mémoire (Singleton).
    Même principe que Whisper : évite de recharger le modèle à chaque requête.
    """
    classificateur = pipeline(
        "image-classification",
        model="google/vit-base-patch16-224"
    )
    return classificateur

def analyser_image(bytes_image: bytes) -> dict:
    """
    Prend les bytes bruts d'une image (reçus depuis l'API) et retourne
    un diagnostic (label + score de confiance).
    """
    classificateur = charger_modele_vision()

    # Conversion des bytes bruts en objet Image (Pillow)
    image = Image.open(io.BytesIO(bytes_image)).convert("RGB")

    resultats = classificateur(image)

    # On garde le résultat le plus probable
    meilleur_resultat = resultats[0]

    diagnostic = {
        "label_detecte": meilleur_resultat["label"],
        "score_confiance": round(meilleur_resultat["score"], 3)
    }
    return diagnostic

