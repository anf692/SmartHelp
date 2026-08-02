import io
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from services.config import MAX_FILE_SIZE_MB


def valider_taille(contents: bytes):
    """Vérifie que le fichier ne dépasse pas la taille maximale autorisée."""
    taille_mo = len(contents) / (1024 * 1024)
    if taille_mo > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop lourd ({taille_mo:.2f} Mo). Limite : {MAX_FILE_SIZE_MB} Mo."
        )


def valider_et_ouvrir_image(contents: bytes) -> Image.Image:
    """
    Valide un fichier image reçu (taille + intégrité réelle) et le retourne
    prêt à l'emploi en RGB.

    Raises:
        HTTPException 400 si le fichier est trop lourd, n'est pas
        une image valide, ou illisible.
    """
    valider_taille(contents)

    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # vérifie l'intégrité sans charger toute l'image

        # verify() invalide l'objet -> on doit rouvrir l'image pour l'utiliser
        image = Image.open(io.BytesIO(contents)).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Le fichier envoyé n'est pas une image valide."
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Erreur lors de la lecture de l'image."
        )

    return image

