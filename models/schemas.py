from pydantic import BaseModel
from typing import Optional

class ReponseTicketSupport(BaseModel):
    """
    Structure du JSON final retourné par l'API après analyse
    d'une réclamation (audio et/ou image et/ou texte).
    """
    texte_transcrit: Optional[str] = None
    diagnostic_image: Optional[dict] = None
    regle_appliquee: Optional[str] = None
    statut_propose: str

    