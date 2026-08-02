# SmartHelp – Micro-service de Support Client Multimodal (Audio & Vision)

SmartHelp est une API construite avec **FastAPI** qui automatise la première analyse des réclamations client dans un contexte e-commerce. Un client peut envoyer un **message vocal**, une **photo** de produit endommagé, et/ou un **texte** décrivant son problème. L'API transcrit l'audio, analyse l'image, interroge une base de connaissances interne (politique de retour/CGV) via un système **RAG** (Retrieval-Augmented Generation), et retourne un diagnostic structuré en JSON pour orienter instantanément l'équipe support.

---

## Table des matières

1. [Contexte du projet](#contexte-du-projet)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture du projet](#architecture-du-projet)
4. [Choix techniques](#choix-techniques)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Lancement de l'API](#lancement-de-lapi)
8. [Utilisation via Swagger](#utilisation-via-swagger)
9. [Détail des modules](#détail-des-modules)
10. [Gestion de projet (Git Flow & Kanban)](#gestion-de-projet-git-flow--kanban)
11. [Difficultés rencontrées et solutions](#difficultés-rencontrées-et-solutions)
12. [Limites connues et pistes d'amélioration](#limites-connues-et-pistes-damélioration)

---

## Contexte du projet

Dans une entreprise e-commerce, le service client reçoit une grande quantité de réclamations via des applications de messagerie (notes vocales, photos). L'équipe support perd un temps précieux à tout écouter, regarder, puis chercher manuellement dans les conditions générales de vente (CGV) ou la FAQ interne la règle applicable. SmartHelp automatise cette première étape d'analyse pour aiguiller instantanément les équipes vers la bonne décision (remboursement, vérification manuelle, refus, etc.).

## Fonctionnalités

- **Endpoint unique d'ingestion** (`POST /support-ticket`) acceptant, dans une seule requête `multipart/form-data`, un fichier audio (`.mp3`/`.wav`), une image (`.png`/`.jpg`) et un texte descriptif, tous **optionnels** et combinables.
- **Transcription audio (ASR)** via le modèle `openai/whisper-small`, chargé une seule fois en mémoire (singleton via `@lru_cache`).
- **Analyse visuelle** via un modèle de classification d'image (`google/vit-base-patch16-224`), également chargé en singleton.
- **Recherche documentaire (RAG)** : le texte transcrit ou fourni interroge une base de connaissances interne (politique de retour/CGV) stockée dans une base vectorielle Chroma, avec des embeddings spécialisés en français (`dangvantuan/sentence-camembert-base`).
- **Diagnostic structuré en JSON** combinant : le texte transcrit, le diagnostic de l'image, la règle interne trouvée, et un statut proposé (`Remboursable`, `À vérifier`, `Refusé`, `En attente de justificatifs`).
- **Gestion propre des fichiers temporaires** : les fichiers audio reçus sont écrits temporairement sur disque puis systématiquement supprimés après traitement.

## Architecture du projet

```
smarthelp/
│
├── main.py                    # Point d'entrée de l'application FastAPI
│
├── routes/
│   └── support_ticket.py      # Route POST /support-ticket (orchestration)
│
├── services/
│   ├── asr_service.py         # Transcription audio (Whisper, singleton)
│   ├── vision_service.py      # Classification d'image (ViT, singleton)
│   └── rag_service.py         # Chunking, embeddings, recherche sémantique
│
├── rag/
│   ├── knowledge_base.txt     # Base de connaissances (politique de retour/CGV)
│   └── vectorstore/           # Stockage vectoriel Chroma (généré automatiquement)
│
├── models/
│   └── schemas.py             # Schéma Pydantic de la réponse JSON
│
├── temp_files/                 # Dossier temporaire pour fichiers audio reçus (nettoyé après usage)
│
├── .env.example                 # Exemple de variables d'environnement
├── .gitignore                   # Fichiers/dossiers exclus du dépôt Git
├── requirements.txt              # Dépendances Python du projet
└── README.md                     # Ce document
```

Cette organisation en couches sépare clairement :
- **`routes/`** : ce que l'extérieur appelle (l'URL de l'API)
- **`services/`** : la logique métier et IA, un fichier par domaine (audio, image, RAG), afin que plusieurs personnes puissent travailler en parallèle sans se marcher dessus (voir section Git Flow)
- **`rag/`** : les données et le stockage vectoriel
- **`models/`** : la structure des données échangées (entrée/sortie de l'API)

## Choix techniques

| Besoin | Modèle/Outil choisi | Justification |
|---|---|---|
| Transcription audio | `openai/whisper-small` | Bon compromis qualité/légèreté, gratuit, tourne en local (CPU) |
| Classification d'image | `google/vit-base-patch16-224` | Modèle Vision Transformer pré-entraîné, gratuit, démontre le mécanisme de classification demandé par le brief |
| Embeddings pour le RAG | `dangvantuan/sentence-camembert-base` | Modèle spécialisé français ; un premier essai avec `all-MiniLM-L6-v2` (modèle généraliste) donnait des correspondances sémantiques imprécises sur des formulations naturelles en français (voir section Difficultés rencontrées) |
| Base vectorielle | Chroma | Simple à utiliser en local, persistance sur disque, pas de service externe payant |
| Framework API | FastAPI | Gestion native de `multipart/form-data`, validation via Pydantic, documentation Swagger automatique |

Aucun service payant n'est utilisé : l'ensemble du pipeline (ASR, Vision, RAG) fonctionne entièrement en local avec des modèles gratuits issus de Hugging Face.

## Installation

### Prérequis
- Python 3.10 ou supérieur
- `pip` et `venv`

### Étapes

```bash
# 1. Cloner le dépôt
git https://github.com/anf692/SmartHelp.git
cd SmartHelp

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Sur Linux/Mac
# venv\Scripts\activate          # Sur Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Copier le fichier d'exemple et l'adapter si nécessaire :

```bash
cp .env.example .env
```

Le fichier `.env.example` contient les chemins par défaut utilisés par l'application (base de connaissances, dossier de stockage vectoriel, dossier temporaire). Aucune clé d'API payante n'est nécessaire, tous les modèles utilisés sont gratuits et publics sur Hugging Face.

## Lancement de l'API

```bash
uvicorn main:app --reload
```

L'API est alors accessible sur : `http://127.0.0.1:8000`

## Utilisation via Swagger

Rendez-vous sur `http://127.0.0.1:8000/docs` pour accéder à l'interface Swagger interactive.

1. Ouvrez la route `POST /support-ticket`
2. Cliquez sur **"Try it out"**
3. Renseignez au choix : un fichier audio, une image, un champ texte (ou une combinaison des trois)
4. **Important** : si vous ne souhaitez pas remplir le champ `texte`, laissez-le réellement vide plutôt que de laisser le mot `string` pré-rempli par Swagger, sous peine de fausser l'analyse
5. Cliquez sur **"Execute"** pour recevoir le diagnostic JSON

### Exemple de réponse

```json
{
  "texte_transcrit": "mon colis est arrivé cassé",
  "diagnostic_image": {
    "label_detecte": "carton",
    "score_confiance": 0.87
  },
  "regle_appliquee": "Règle 1.1 (Casse / Dommage visible) : ...",
  "statut_propose": "Remboursable"
}
```

## Détail des modules

### Module ASR (`services/asr_service.py`)

Charge le modèle Whisper une seule fois grâce au décorateur `@lru_cache`, évitant de recharger un modèle volumineux à chaque requête (impact RAM et latence). La fonction `transcrire_audio` prend un **chemin de fichier** (Whisper nécessite un fichier sur disque) et retourne le texte transcrit.

### Module Vision (`services/vision_service.py`)

Charge le modèle ViT également en singleton. Contrairement à l'audio, l'image est traitée directement à partir des **bytes bruts** en mémoire (via `Pillow`/`io.BytesIO`), sans écriture sur disque.

### Module RAG (`services/rag_service.py`)

1. Charge et découpe (`chunk_size=500`, `chunk_overlap=50`) le document de politique de retour
2. Génère les embeddings avec CamemBERT et les stocke dans Chroma (persistant sur disque, évitant de recalculer les embeddings à chaque redémarrage)
3. Effectue une recherche sémantique (`similarity_search`) pour retrouver les règles les plus pertinentes par rapport au texte de la réclamation

### Orchestration (`routes/support_ticket.py`)

Reçoit la requête multipart, traite conditionnellement chaque type de contenu fourni (audio → transcription, image → diagnostic, texte → nettoyage), interroge le RAG avec le texte disponible, détermine un statut proposé, et retourne le JSON structuré défini dans `models/schemas.py`.

## Gestion de projet (Git Flow & Kanban)

Le projet suit une stratégie **Git Flow** stricte :

- `main` : version stable et finale du projet
- `develop` : branche d'intégration de toutes les fonctionnalités
- `feature/...` : une branche dédiée par fonctionnalité (ex. `feature/rag-setup`, `feature/asr-whisper`, `feature/vision-vit`, `feature/endpoint-support-ticket`)

Aucun commit n'est effectué directement sur `main` ou `develop` : chaque fonctionnalité est développée sur sa propre branche, puis fusionnée après validation.

Le suivi des tâches est assuré via un tableau Kanban (Backlog → In Progress → Review → Done) : *[insérer ici le lien vers votre tableau Trello/GitHub Projects]*.

## Difficultés rencontrées et solutions

- **Encodage du fichier de connaissances** : le document source contenait des caractères mal encodés (ex. `endommagÃ©` au lieu de `endommagé`). Résolu en ré-enregistrant le fichier en UTF-8 explicite.
- **Doublons dans la base vectorielle** : au premier essai, chaque redémarrage recréait les embeddings et les ajoutait à une base déjà existante, provoquant des doublons et des résultats de recherche incohérents. Résolu en vérifiant l'existence du dossier de stockage vectoriel avant de recréer les embeddings.
- **Imprécision sémantique du premier modèle d'embedding** : `all-MiniLM-L6-v2` (modèle généraliste) associait parfois des réclamations à des règles incorrectes sur des formulations naturelles en français (ex. confondait "colis cassé" avec "colis perdu"). Remplacé par `dangvantuan/sentence-camembert-base`, spécialisé en français, pour améliorer la pertinence des résultats.
- **Champ texte non réellement vide dans Swagger** : Swagger pré-remplit certains champs avec le mot `string` par défaut ; si l'utilisateur ne l'efface pas, l'API le traite comme un vrai texte. Une étape de nettoyage a été ajoutée pour ignorer cette valeur par défaut.

## Limites connues et pistes d'amélioration

- Le modèle de classification d'image (`google/vit-base-patch16-224`) est un modèle généraliste et n'est pas spécifiquement entraîné pour détecter des défauts produits ; une piste d'amélioration serait le fine-tuning sur un jeu de données de produits endommagés.
- La logique de détermination du statut final (`statut_propose`) est actuellement basée sur une recherche de mots-clés simples (ex. présence du mot "Remboursable") dans la règle trouvée ; elle pourrait être affinée avec une extraction plus structurée des statuts associés à chaque règle.
- L'ensemble du pipeline tourne actuellement en local sur CPU ; les temps de réponse pourraient être optimisés avec un déploiement sur GPU pour un usage à plus grande échelle.