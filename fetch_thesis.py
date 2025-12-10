#!/usr/bin/env python3
import requests
import json
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import time

BASE_URL = "https://apd.sgh.waw.pl/catalogue/search/simple/"
PARAMS = {
    "query": "rubach",
    "type": "all",
    "limit": 40
}
OUTPUT_FILE = "sgh_theses_rubach.json"


def get_page(page_num):
    params = PARAMS.copy()
    params["page"] = page_num
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    return resp.text


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    theses = []
    # Adjust this selector based on actual table/list structure:
    # For example, many such catalogues use <table> with <tr> rows.
    table = soup.find("table")
    if not table:
        return theses

    for tr in table.find_all("tr"):
        # you may need to skip header rows
        tds = tr.find_all("td")
        if not tds:
            continue
        # Example: first td = title, or there is a link
        link_tag = tr.find("a", href=True)
        if not link_tag:
            continue
        title = link_tag.get_text(strip=True)
        href = link_tag["href"]
        full_url = urljoin(BASE_URL, href)
        # Optionally extract additional columns:
        # e.g. author, year, etc. Example placeholders:
        # author = tds[1].get_text(strip=True)  # adjust index
        # year   = tds[2].get_text(strip=True)
        theses.append({
            "title": title,
            "url": full_url,
            # "author": author,
            # "year": year
        })
    return theses


def has_next_page(soup):
    # Adjust this depending on the site’s pagination — e.g. a “Next” link / button
    next_link = soup.find("a", text="Next")  # or appropriate label
    return next_link is not None


def main():
    all_theses = []
    page = 1
    while True:
        print(f"Fetching page {page}...")
        html = get_page(page)
        soup = BeautifulSoup(html, "html.parser")
        page_theses = parse_page(html)
        if not page_theses:
            print("No theses found on this page — stopping.")
            break
        all_theses.extend(page_theses)

        # Try to detect if there is a next page:
        # Either by link, or by checking if number of rows < limit.
        # Here, naive approach: if we got exactly limit items — assume maybe more.
        if len(page_theses) < PARAMS["limit"]:
            break
        page += 1
        time.sleep(1)  # polite delay

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_theses, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_theses)} theses to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
