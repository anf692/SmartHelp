from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

CHEMIN_BASE_CONNAISSANCE = "rag/document.txt"
CHEMIN_VECTORSTORE = "rag/vectorstore"

def charger_et_decouper_document():
    """Charge le fichier CGV et le découpe en petits morceaux (chunks)."""
    chargeur = TextLoader(CHEMIN_BASE_CONNAISSANCE, encoding="utf-8")
    documents = chargeur.load()

    decoupeur = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    morceaux = decoupeur.split_documents(documents)
    return morceaux


def creer_ou_charger_vectorstore():
    """Crée la base vectorielle si elle n'existe pas, sinon la recharge sans dupliquer."""
    modele_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if os.path.exists(CHEMIN_VECTORSTORE) and os.listdir(CHEMIN_VECTORSTORE):
        # Le vectorstore existe déjà sur disque → on le recharge simplement
        base_vectorielle = Chroma(
            persist_directory=CHEMIN_VECTORSTORE,
            embedding_function=modele_embeddings
        )
    else:
        # Première fois → on crée le vectorstore
        morceaux = charger_et_decouper_document()
        base_vectorielle = Chroma.from_documents(
            documents=morceaux,
            embedding=modele_embeddings,
            persist_directory=CHEMIN_VECTORSTORE
        )
    return base_vectorielle


def rechercher_regle_applicable(texte_reclamation: str, base_vectorielle, k: int = 2):
    """
    Cherche dans la base de connaissances les règles les plus pertinentes
    par rapport au texte de la réclamation (transcrit ou envoyé en texte).
    """
    resultats = base_vectorielle.similarity_search(texte_reclamation, k=k)

    if not resultats:
        return "Aucune règle trouvée - à vérifier manuellement."

    regles_trouvees = "\n\n".join([resultat.page_content for resultat in resultats])
    return regles_trouvees
