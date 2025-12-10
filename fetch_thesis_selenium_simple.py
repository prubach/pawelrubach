from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
import time, json

driver = webdriver.Edge()  # Chrome/Firefox also possible
driver.get("https://apd.sgh.waw.pl")

print("LOGIN MANUALLY — including MFA")
input("Press Enter when logged in...")

# After login → browser has full access
driver.get("https://apd.sgh.waw.pl/catalogue/search/simple/?query=rubach&type=all&limit=40")

html = driver.page_source
with open("page.html", "w", encoding="utf8") as f:
    f.write(html)

print("✔ Page downloaded")
driver.quit()
