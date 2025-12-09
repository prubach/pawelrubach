import requests, yaml

ORCID = "0000-0001-5487-609X"
api_url = f"https://pub.orcid.org/v3.0/{ORCID}/works"
headers = {"Accept": "application/json"}

response = requests.get(api_url, headers=headers)
works = response.json().get("group", [])

publications = []

for w in works:
    summary = w.get("work-summary", [{}])[0]
    title = summary.get("title", {}).get("title", {}).get("value", "No title")
    year = summary.get("publication-date", {}).get("year", {}).get("value", None)
    journal_title = summary.get("journal-title", {})
    if journal_title:
        journal = journal_title.get("value", None)
    link = summary.get("external-ids", {}).get("external-id", [])
    doi = None

    for i in link:
        if i.get("external-id-type") == "doi":
            doi = i.get("external-id-value")

    publications.append({
        "title": title,
        "year": year,
        "journal": journal,
        "doi": doi
    })

with open("_data/orcid_publications.yml", "w") as f:
    yaml.dump(publications, f)
print("ORCID publications updated.")
