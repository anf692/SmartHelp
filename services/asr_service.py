from functools import lru_cache
from transformers import pipeline

@lru_cache()
def charger_modele_whisper():
    """
    Charge le modèle Whisper une seule fois en mémoire (Singleton).
    Grâce à @lru_cache, si cette fonction est appelée plusieurs fois,
    le modèle n'est chargé qu'à la première fois — les appels suivants
    réutilisent directement le modèle déjà en mémoire.
    """
    transcripteur = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small"
    )
    return transcripteur

def transcrire_audio(chemin_fichier_audio: str) -> str:
    """
    Prend le chemin d'un fichier audio (.mp3 ou .wav) et retourne le texte transcrit.
    """
    transcripteur = charger_modele_whisper()
    resultat = transcripteur(chemin_fichier_audio)
    texte_transcrit = resultat["text"]
    return texte_transcrit

