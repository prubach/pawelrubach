import json
from bs4 import BeautifulSoup
import requests
from time import sleep

# -------- CONFIG -------- #
MASTER_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=master&limit=100"
BACHELOR_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=licentiate"

OUTPUT_FILE = "rubach_theses.json"

# -------- SCRAPER -------- #
def get_year_from_subpage(link):
    """Open thesis detail page and extract the year."""
    try:
        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        year_tag = soup.find("div", class_="col-lg-3 d-flex align-items-start mb-3")
        if year_tag:
            text = year_tag.get_text(strip=True)
            # Extract 4-digit year if present
            for token in text.split():
                if token.isdigit() and len(token) == 4:
                    return token
        return None
    except:
        return None


def scrape_list(url, category):
    """Scrape thesis list for one category"""
    print(f"Scraping: {category.upper()} - {url}")
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    entries = []

    # each result is inside <div class="list-group-item p-3 catalogue-entry">...
    for item in soup.select("div.catalogue-entry"):
        title = item.find("h5").get_text(strip=True)

        author = supervisor = None

        info_blocks = item.select("div.catalogue-entry__header span")
        for block in info_blocks:
            text = block.get_text(strip=True)
            if "Author" in text or "Autor" in text:
                author = text.split(":")[-1].strip()
            if "Supervisor" in text or "Promotor" in text:
                supervisor = text.split(":")[-1].strip()

        # follow link to detail page → retrieve year
        link = item.find("a", href=True)["href"]
        full_url = "https://apd.sgh.waw.pl" + link

        year = get_year_from_subpage(full_url)
        sleep(0.8)  # be polite

        entries.append({
            "title": title,
            "author": author,
            "supervisor": supervisor,
            "link": full_url,
            "year": year,
            "category": category
        })

        print(f"   ✔ {title} ({year})")

    return entries


# -------- MAIN -------- #
all_results = []
all_results += scrape_list(MASTER_URL, "master")
all_results += scrape_list(BACHELOR_URL, "bachelor")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4, ensure_ascii=False)

print(f"\nSaved {len(all_results)} theses → {OUTPUT_FILE}")
