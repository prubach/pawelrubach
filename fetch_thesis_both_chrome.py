import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ===================== CONFIG ===================== #
CHROME_PROFILE_PATH = ".chrome_profile"     # <-- adjust path
PROFILE_NAME = "Default"                                      # <-- your Chrome profile name

MASTER_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=master&limit=100"
BACHELOR_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=licentiate"

OUTPUT_FILE = "rubach_theses.json"

WAIT_BEFORE_SCRAPING = 45   # time for you to pass MFA after browser loads
OPEN_DELAY = 1.2            # delay per subpage visit

# ================== SELENIUM SETUP ================= #
options = Options()
options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
options.add_argument(f"--profile-directory={PROFILE_NAME}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

# Uncomment if you want silent/headless scraping:
# options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

print("🌍 Chrome launched using your session...")
print("👉 Complete MFA manually if required.")
time.sleep(WAIT_BEFORE_SCRAPING)  # pause to let you login

# ================= FUNCTIONS ================== #

def extract_year():
    """Extract 4-digit year if present anywhere on the page."""
    try:
        blocks = driver.find_elements(By.CSS_SELECTOR, ".col-lg-3.d-flex.align-items-start.mb-3")
        for b in blocks:
            txt = b.text.strip()
            for token in txt.split():
                if token.isdigit() and len(token) == 4:
                    return token
    except:
        return None


def scrape(url, category):
    print(f"\n===== SCRAPING {category.upper()} =====")
    driver.get(url)
    time.sleep(4)

    entries = driver.find_elements(By.CSS_SELECTOR, "div.catalogue-entry")
    dataset = []

    for item in entries:
        title = item.find_element(By.TAG_NAME, "h5").text.strip()

        author = supervisor = None
        spans = item.find_elements(By.CSS_SELECTOR, "span")
        for s in spans:
            text = s.text.strip()
            if "Autor" in text or "Author" in text:
                author = text.split(":")[-1].strip()
            if "Promotor" in text or "Supervisor" in text:
                supervisor = text.split(":")[-1].strip()

        link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

        # ⏩ Visit subpage to get year
        driver.get(link)
        time.sleep(OPEN_DELAY)
        year = extract_year()

        dataset.append({
            "title": title,
            "author": author,
            "supervisor": supervisor,
            "year": year,
            "link": link,
            "category": category
        })

        print(f"   ✔ {title}  ({year})")
        driver.back()
        time.sleep(OPEN_DELAY)

    return dataset


# ============= RUN ============= #
results = []
results += scrape(MASTER_URL, "master")
results += scrape(BACHELOR_URL, "bachelor")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n📁 Saved {len(results)} theses → {OUTPUT_FILE}")
driver.quit()
