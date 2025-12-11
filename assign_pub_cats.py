import json
from pathlib import Path

# Paths
PUB_FILE = Path("_data/publications.json")
CAT_FILE = Path("_data/publications_categories.json")

# Category rules based on journal name
CATEGORY_RULES = {
    "Nucleic Acids Research": ["Structural Biology"],
    "Briefings in Bioinformatics": ["Structural Biology"],
    "Protein Science": ["Structural Biology"],
    "IUCrJ": ["Structural Biology"],
    "Kinases and Phosphatases": ["Structural Biology"],
    "Acta Crystallographica Section D Structural Biology": ["Structural Biology"],
    "Expert Opinion on Drug Discovery": ["Structural Biology"],
    "Wiadomości Statystyczne": ["Machine Learning"],
    "Artificial Intelligence and Soft Computing": ["Machine Learning"],
    "Metody Ilościowe w Badaniach Ekonomicznych": ["Machine Learning"],
    "Lecture Notes in Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics)": ["Machine Learning"],
    "PEARC '25: Practice and Experience in Advanced Research Computing": ["Distributed Computing"],
    "Proceedings of the International Conference on Parallel Processing Workshops": ["Distributed Computing"],
}

def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    publications = load_json(PUB_FILE)
    category_data = load_json(CAT_FILE)

    # Ensure top-level keys exist
    category_data.setdefault("categories", [])
    category_data.setdefault("assignments", {})

    assignments = category_data["assignments"]
    categories = set(category_data["categories"])

    updated = 0

    for p in publications:
        orcid = p.get("id")
        journal = p.get("journal", "").strip()

        if not orcid:
            continue  # Skip if missing ORCID

        if journal in CATEGORY_RULES:
            new_cats = CATEGORY_RULES[journal]
            categories.update(new_cats)

            # Assign or extend
            current = set(assignments.get(orcid, []))
            before = current.copy()

            current.update(new_cats)
            assignments[orcid] = sorted(current)

            if current != before:
                updated += 1

    # Save changes
    category_data["categories"] = sorted(categories)
    save_json(CAT_FILE, category_data)

    print(f"Updated categories for {updated} publications.")
    print(f"Total categories: {len(categories)}")

if __name__ == "__main__":
    main()
