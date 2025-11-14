import wikipedia
import os
import json

def collect_wikipedia_data(query, lang='fr', output_dir='/app/raw_data', num_articles=5):
    """
    Collecte des articles Wikipedia basés sur une requête et les sauvegarde au format texte.
    """
    wikipedia.set_lang(lang)
    try:
        results = wikipedia.search(query, results=num_articles)
        collected_data = []
        for title in results:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                # Save as plain text
                filename = os.path.join(output_dir, f"wikipedia_{lang}_{title.replace(' ', '_')}.txt")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(page.content)
                print(f"Article sauvegardé : {filename}")

                # Optional: Save as JSONL (for future instruction tuning)
                jsonl_filename = os.path.join(output_dir, f"wikipedia_{lang}.jsonl")
                with open(jsonl_filename, 'a', encoding='utf-8') as f:
                    json_entry = {
                        "instruction": f"Décris l'article Wikipedia sur {title}.",
                        "input": "", # For now, input is empty, content is output
                        "output": page.content,
                        "source": "wikipedia",
                        "era": "mixed", # Era might vary, can refine later
                        "language": lang,
                        "title": title,
                        "url": page.url
                    }
                    f.write(json.dumps(json_entry, ensure_ascii=False) + '\n')
                
                collected_data.append({"title": title, "url": page.url, "length": len(page.content)})

            except wikipedia.exceptions.PageError:
                print(f"PageError pour l'article : {title}")
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"DisambiguationError pour l'article : {title}. Options : {e.options}")
            except Exception as e:
                print(f"Erreur inattendue lors de la récupération de {title}: {e}")
        
        return collected_data

    except Exception as e:
        print(f"Erreur lors de la recherche Wikipedia pour '{query}': {e}")
        return []

if __name__ == '__main__':
    # Créer le répertoire de sortie si inexistant
    output_base_dir = '/app/raw_data'
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    print("Début de la collecte de données Wikipedia...")
    
    # Exemples de requêtes basées sur les thèmes OSS 117
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
        "Politique française XXe siècle"
    ]

    all_collected_articles = []
    for q in queries:
        print(f"Recherche pour : '{q}'")
        articles = collect_wikipedia_data(q, lang='fr', output_dir=output_base_dir, num_articles=3)
        all_collected_articles.extend(articles)
    
    print("\n--- Résumé de la collecte ---")
    if all_collected_articles:
        for article in all_collected_articles:
            print(f"- {article['title']} ({article['url']}) - {article['length']} caractères")
    else:
        print("Aucun article n'a été collecté.")
    print("Collecte de données Wikipedia terminée.")