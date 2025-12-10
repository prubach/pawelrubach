#!/usr/bin/env python3
"""
Selenium scraper for APD SGH thesis list (including login + pagination)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time


#START_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=all&limit=40"
START_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=master&limit=100"
START_URL_LIC = "https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=licentiate"
OUTFILE = "theses_sgh.json"


def scrape_all_pages(driver):
    results = []
    page = 1

    for url in [START_URL, START_URL_LIC]:
        print(f"🔎 Scraping page {page} …")
        driver.get(f"{url}")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        table = soup.find("table")
        if not table:
            print("No table → stopping")
            break

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:   # skip header
                continue

            link = row.find("a", href=True)
            if not link:
                continue

            results.append({
                "title": link.text.strip(),
                "url": link["href"],
                "author": cols[1].text.strip() if len(cols) > 1 else None,
                "year": cols[2].text.strip() if len(cols) > 2 else None,
                "supervisor": cols[3].text.strip() if len(cols) > 3 else None
            })

        print(f" → collected {len(results)}")

        # If less than 40 rows → no more pages
        if len(table.find_all("tr")) < 40:
            break

        page += 1

    return results

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

def init_driver(headless=False, user_profile=False):
    options = ChromeOptions()

    # Recommended stability flags
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")  # modern headless mode
        options.add_argument("--window-size=1920,1080")

    # optional: persist Microsoft login, skip entering credentials every time
    if user_profile:
        options.add_argument(r"--user-data-dir=./chrome_profile")  # will be created automatically

    driver = webdriver.Chrome(options=options)  # ⬅ correct usage (no .capabilities error)
    return driver

def main():
    driver = init_driver(headless=False, user_profile=True)
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://apd.sgh.waw.pl")

    print("\n🟡 Log in manually (Microsoft + MFA).")
    print("   When you land on the APD homepage → press ENTER here.\n")
    input("Press ENTER when logged in fully… ")

    results = scrape_all_pages(driver)
    driver.quit()

    with open(OUTFILE, "w", encoding="utf8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✔ Saved {len(results)} theses → {OUTFILE}")


if __name__ == "__main__":
    main()
