from concurrent.futures import ThreadPoolExecutor
from data_scripts import wikipedia_raw_data as wiki_data
from data_scripts import huggingface_raw_data as hf_data


output_base_dir = '/app/raw_data'

queries = [
        "Guerre froide",
        "Espionnage français",
        "Services secrets français",
        "Histoire de la France 1950",
        "Histoire de la France 1960",
        "Histoire de la France 1970",
        "Histoire de la France 1980",
        "Agent secret",
        "Opération secrète",
        "Espion",
        "Politique française XXe siècle",
        "Géopolitique XXe siècle",
        "Relations internationales XXe siècle",
        "Guerre d'Algérie",
        "Décolonisation",
        "OTAN",
        "Pacte de Varsovie",
        "Crise des missiles de Cuba",
        "Mur de Berlin",
        "CIA",
        "KGB",
        "DGSE",
        "Guerre du Vietnam",
        "Dissuasion nucléaire",
        "Espionnage pendant la guerre froide"
]

def process_query(q):
    print(f"🚀 Lancement recherche : '{q}'")
    return wiki_data.collect_wikipedia_data(q, lang='fr', output_dir=output_base_dir, num_articles=3)

# Utilisation de 5 workers en parallèle
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_query, queries))

# Aplatir les résultats pour le résumé
all_articles = [item for sublist in results for item in sublist]

print(f"\n--- Total articles collectés : {len(all_articles)} ---")

# --- 2. Collecte Hugging Face ---
print("\n--- 🤗 DÉBUT COLLECTE HUGGING FACE ---")

# Liste de vos datasets (Exemple avec un dataset public français)
# Remplacez par votre dataset: "votre-nom-utilisateur/votre-dataset"
hf_datasets_to_load = [
    # {"name": "pleiade/french-pd-books", "subset": None, "col": "main_text"},
    # {"name": "fquad", "subset": None, "col": "context"},
    # Exemple générique :
    {"name": "pleiade/french-pd-books", "subset": None, "col": "text"}, 
    {"name": "flaubert/flaubert_base_cased", "subset": None, "col": "text"}
]

for ds in hf_datasets_to_load:
    hf_data.collect_huggingface_data(
        dataset_name=ds['name'],
        subset=ds['subset'],
        text_column=ds['col'],
        output_dir=output_base_dir
    )

print("\n🎉 Collecte de toutes les données terminée.")
