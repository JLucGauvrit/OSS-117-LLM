from datasets import load_dataset
import os
import json

def collect_huggingface_data(dataset_name, subset=None, split='train', text_column='text', output_dir='/app/raw_data'):
    """
    Télécharge un dataset Hugging Face et le convertit au format JSONL du projet.
    """
    print(f"📥 Téléchargement du dataset : {dataset_name}...")
    
    try:
        # Chargement du dataset (gère le cache automatiquement)
        dataset = load_dataset(dataset_name, subset, split=split)
        
        # Création du fichier de sortie
        safe_name = dataset_name.replace("/", "_")
        output_file = os.path.join(output_dir, f"hf_{safe_name}.jsonl")
        
        count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            for row in dataset:
                # Récupération du contenu principal (adapter 'text_column' selon le dataset)
                content = row.get(text_column, "")
                if not content:
                    continue

                # Formatage uniforme avec vos données Wikipedia
                json_entry = {
                    "instruction": "Contenu brut importé de Hugging Face.",
                    "input": "",
                    "output": content,
                    "source": f"huggingface/{dataset_name}",
                    "era": "mixed",
                    "language": "fr", # À adapter si multilingue
                    "original_row": row # Garde les métadonnées au cas où
                }
                f.write(json.dumps(json_entry, ensure_ascii=False) + '\n')
                count += 1
        
        print(f"✅ {count} entrées sauvegardées dans {output_file}")
        return count

    except Exception as e:
        print(f"❌ Erreur lors de l'import de {dataset_name}: {e}")
        return 0
    