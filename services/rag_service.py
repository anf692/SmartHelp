from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

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
    """Crée la base vectorielle Chroma si elle n'existe pas encore, sinon la recharge."""
    modele_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    morceaux = charger_et_decouper_document()

    base_vectorielle = Chroma.from_documents(
        documents=morceaux,
        embedding=modele_embeddings,
        persist_directory=CHEMIN_VECTORSTORE
    )
    return base_vectorielle


