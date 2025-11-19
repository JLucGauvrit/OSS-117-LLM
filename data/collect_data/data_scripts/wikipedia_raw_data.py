import wikipedia
import os
import json
import re
import time

# Sections à exclure pour un dataset LLM plus propre
EXCLUDE_SECTIONS = ["Voir aussi", "Notes et références", "Bibliographie", "Liens externes"]

def clean_content(content):
    """Coupe le contenu dès qu'une section 'parasite' est rencontrée."""
    for section in EXCLUDE_SECTIONS:
        # Recherche de la section (ex: "== Voir aussi ==")
        pattern = f"== {section} =="
        if pattern in content:
            content = content.split(pattern)[0]
    return content.strip()

def collect_wikipedia_data(query, lang='fr', output_dir='/app/raw_data', num_articles=5):
    wikipedia.set_lang(lang)
    # Définit un user-agent pour éviter le blocage (format: Projet/Version Contact)
    wikipedia.set_user_agent("OSS-117-LLM/1.0 (contact@example.com)")
    
    collected_data = []
    
    try:
        results = wikipedia.search(query, results=num_articles)
        
        for title in results:
            safe_title = title.replace(' ', '_').replace('/', '-')
            filename = os.path.join(output_dir, f"wikipedia_{lang}_{safe_title}.txt")
            
            # Évite de refaire une requête si le fichier existe déjà
            if os.path.exists(filename):
                print(f"♻️  Existant : {title}")
                continue

            try:
                page = wikipedia.page(title, auto_suggest=False)
                cleaned_text = clean_content(page.content)

                # Sauvegarde texte brut
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                
                # Sauvegarde JSONL (plus riche)
                jsonl_filename = os.path.join(output_dir, f"wikipedia_{lang}.jsonl")
                with open(jsonl_filename, 'a', encoding='utf-8') as f:
                    json_entry = {
                        "instruction": f"Explique le concept de {title} dans le contexte de {query}.",
                        "input": "",
                        "output": cleaned_text,
                        "source": "wikipedia",
                        "url": page.url
                    }
                    f.write(json.dumps(json_entry, ensure_ascii=False) + '\n')
                
                print(f"✅ Sauvegardé : {title}")
                collected_data.append({"title": title, "length": len(cleaned_text)})
                
                # Petite pause pour respecter l'API
                time.sleep(1)

            except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError) as e:
                print(f"⚠️ Erreur sur {title}: {e}")
            except Exception as e:
                print(f"❌ Erreur critique sur {title}: {e}")

    except Exception as e:
        print(f"Erreur recherche '{query}': {e}")
    
    return collected_data
