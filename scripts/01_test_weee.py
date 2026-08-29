from playwright.sync_api import sync_playwright


START_URL = "https://www.weee.com/en/grocery-near-me/asian-supermarket-in-usa/korean-store"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(START_URL)

    print(page.title())

    browser.close()