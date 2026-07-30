# voir_chunks.py
from services.rag_service import charger_et_decouper_document

morceaux = charger_et_decouper_document()
for i, morceau in enumerate(morceaux):
    print(f"--- Chunk {i} ---")
    print(morceau.page_content)
    print()
    