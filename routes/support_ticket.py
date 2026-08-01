import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from services.asr_service import transcrire_audio
from services.vision_service import analyser_image
from services.rag_service import creer_ou_charger_vectorstore, rechercher_regle_applicable
from models.schemas import ReponseTicketSupport

router = APIRouter()

# Chargement du vectorstore une seule fois au démarrage du module
base_vectorielle = creer_ou_charger_vectorstore()

DOSSIER_TEMPORAIRE = "temp_files"


@router.post("/support-ticket", response_model=ReponseTicketSupport)
async def creer_ticket_support(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    texte: Optional[str] = Form(None)
):
    """
    Reçoit un audio et/ou une image et/ou un texte, analyse le contenu
    et retourne un diagnostic structuré.
    """
    texte_transcrit = None
    diagnostic_image = None

    # On nettoie le texte reçu : on retire les espaces en trop, et on ignore
    # le mot "string" (valeur par défaut de Swagger si le champ n'est pas effacé)
    texte_nettoye = texte.strip() if texte else None
    if texte_nettoye == "string" or texte_nettoye == "":
        texte_nettoye = None
    texte_pour_recherche = texte_nettoye

    # 1. Traitement audio si fourni
    if audio is not None:
        chemin_audio_temp = os.path.join(DOSSIER_TEMPORAIRE, audio.filename)
        with open(chemin_audio_temp, "wb") as fichier_temp:
            shutil.copyfileobj(audio.file, fichier_temp)

        texte_transcrit = transcrire_audio(chemin_audio_temp)
        texte_pour_recherche = texte_transcrit

        os.remove(chemin_audio_temp)  # Nettoyage garanti

    # 2. Traitement image si fournie
    if image is not None:
        bytes_image = await image.read()
        diagnostic_image = analyser_image(bytes_image)

    # 3. Recherche RAG si on a du texte (transcrit ou direct)
    regle_appliquee = None
    if texte_pour_recherche:
        regle_appliquee = rechercher_regle_applicable(texte_pour_recherche, base_vectorielle)

    # 4. Détermination simple du statut proposé
    if regle_appliquee and "Remboursable" in regle_appliquee:
        statut = "Remboursable"
    elif regle_appliquee:
        statut = "À vérifier"
    else:
        statut = "En attente de justificatifs"

    return ReponseTicketSupport(
        texte_transcrit=texte_transcrit,
        diagnostic_image=diagnostic_image,
        regle_appliquee=regle_appliquee,
        statut_propose=statut
    )


