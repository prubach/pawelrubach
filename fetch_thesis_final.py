import json, time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

START_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=all&limit=40"
PROFILE_DIR = "chrome_profile__"  # stores login — after 1st run no login needed

def init_driver(headless=False):
    options = ChromeOptions()

    # Reuse browser session → Microsoft login only once
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    options.add_argument("--disable-popup-blocking")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


# Extract YEAR + other details from subpage
def scrape_thesis_page(driver, url):
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2"))
        )

        meta = {}

        def safe(css):
            try:
                return driver.find_element(By.CSS_SELECTOR, css).text.strip()
            except:
                return None

        meta["title"]     = safe("h2")
        meta["student"]   = safe(".authors")
        meta["abstract"]  = safe("#abstract")
        meta["language"]  = safe(".language")
        meta["keywords"]  = safe(".keywords")
        meta["supervisor"]= safe(".supervisors")

        # year extraction — reliable & official location
        try:
            Details = driver.find_element(By.XPATH, "//strong[contains(text(),'Data złożenia')]/../span").text
            meta["year"] = Details[-4:]
        except:
            meta["year"] = None  # fallback

        return meta

    except Exception as e:
        print("Error subpage:", e)
        return {"title":"", "year":None}


def scrape_all():
    driver = init_driver(headless=False)

    os.makedirs(PROFILE_DIR, exist_ok=True)

    print("\n>>> If Microsoft login screen opens — sign in manually.")
    print(">>> MFA supported — waiting for completion.\n")

    driver.get(START_URL)
    input("Press ENTER after login is complete & search results appear: ")

    all_results = []
    page = 1

    while True:
        print(f"📄 Scraping listing page {page}...")

        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".catalogue-entry"))
        )

        items = driver.find_elements(By.CSS_SELECTOR, ".catalogue-entry h3 > a")

        # Follow each entry to extract full data
        for entry in items:
            url  = entry.get_attribute("href")
            print(" → Details:", url)

            info = scrape_thesis_page(driver, url)
            info["url"] = url
            all_results.append(info)

        # Pagination
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            if "disabled" in next_btn.get_attribute("class"):
                break
            next_btn.click()
            time.sleep(2)
            page += 1
        except:
            break

    driver.quit()
    return all_results


if __name__ == "__main__":
    data = scrape_all()

    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✔ SUCCESS — scraped {len(data)} theses")
    print("📁 Output: students.json")
