# test_rag_manuel.py (juste pour vérifier, tu peux le supprimer après)
from services.rag_service import creer_ou_charger_vectorstore, rechercher_regle_applicable

base = creer_ou_charger_vectorstore()
resultat = rechercher_regle_applicable("mon colis est arrivé cassé", base)
print("la regles est: ",resultat)