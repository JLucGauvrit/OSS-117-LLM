# Collection-Data.md

## Objectif de la collecte

Le but de cette démarche est de constituer un corpus diversifié et riche permettant d’entraîner un modèle de langage large (LLM) from scratch. Nous allons rassembler des données provenant de différentes sources : datasets publics Hugging Face, articles Wikipedia, extraits de films, séries, et livres.

***

## Sources de données

- **Hugging Face Datasets** : Utilisation de jeux de données publics (open source) issus du hub Hugging Face pour récupérer des textes couvrant de nombreux domaines (actualités, discussions Reddit, dialogues, questions/réponses, etc.).[1]
- **Wikipedia** : Extraction des dumps officiels (français/anglais/autres) pour obtenir des textes encyclopédiques variés, propres et structurés.
- **Films, séries et livres** : Sélection d’œuvres du domaine public ou avec droits d’utilisation. Extraction des dialogues, scripts, et passages pour diversifier les styles linguistiques et contextes d’usage.

***

## Format de stockage des données

Toutes les données seront converties en **texte brut** puis stockées principalement en deux formats :

1. **Texte brut (.txt)** : concaténation des paragraphes, dialogues ou documents pour les étapes de prétraitement et de tokenization.
2. **JSONL (JSON Lines)** : un objet JSON par ligne, permettant de structurer chaque exemple pour l’entraînement et de faciliter la gestion de gros volumes de données.

***

## Formats d’étiquetage pour le fine-tuning (Instruction Tuning)

### Format Alpaca

Le format Alpaca (Stanford) est la référence pour l’instruction tuning. Chaque exemple est structuré en trois champs principaux :

```json
{
  "instruction": "Tâche à accomplir exprimée en langage naturel.",
  "input": "Contexte, question ou donnée (facultatif).",
  "output": "Réponse attendue du modèle."
}
```
Exemple :
```json
{"instruction": "Résume le texte suivant.", "input": "Le chat grimpe sur la barrière.", "output": "Un chat grimpe sur une barrière."}
```

### Autres formats

- Pour le pré-entraînement pur (sans instruction/réponse), on stocke souvent le texte brut simplement, parfois en listant chaque document ou paragraphe par ligne ou en objet JSON avec une clé “text”.
- Pour des besoins complexes, chaque objet JSONL peut intégrer d’autres méta-informations (“source”, “id”, “langue”) tout en respectant la compatibilité avec les loaders d’entraînement courants.

***

## Pipeline de traitement et harmonisation

1. **Nettoyage** : suppression des balises, doublons, contenus inutilisables.
2. **Uniformisation** : tout convertir en format texte simple, puis structurer en JSONL (instruction tuning) ou texte classique.
3. **Validation** : contrôle qualité, suppression des entrées corrompues ou incomplètes.
4. **Stockage** : tous les fichiers finaux sont déposés dans des dossiers distincts selon leur source et leur usage (pré-training, instruction tuning, etc.).

***

## Conclusion

Toute la donnée, quel que soit la source, sera ramenée à des formats universels (texte brut et JSONL) adaptés au pré-entraînement et à l’instruction tuning de LLM modernes. Une documentation complémentaire détaillera la provenance, le nettoyage, l’échantillonnage et les choix de structuration si besoin.[2][3][1]

---

[1](https://huggingface.co/datasets/jpacifico/French-Alpaca-dataset-Instruct-55K)
[2](https://docs.anyscale.com/llm/fine-tuning/data-preparation)
[3](https://zackproser.com/blog/how-to-create-a-custom-alpaca-dataset)