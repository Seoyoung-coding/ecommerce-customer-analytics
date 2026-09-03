from playwright.sync_api import sync_playwright
import re


TEST_URL = "https://www.weee.com/en/product/Yupgi-Tteokbokki-Original-/113543"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    try:

        page = browser.new_page()

        page.goto(TEST_URL)

        # 서버 원본 HTML 가져오기
        response = page.request.get(TEST_URL)
        raw_html = response.text()

        # 실제 주간 판매량 표시값 찾기
        weekly_sold_match = re.search(
            r'\\"sold_count_ui\\":\\"([^"]*)\\"',
            raw_html
        )

        weekly_sold_raw = None

        if weekly_sold_match:
            weekly_sold_raw = weekly_sold_match.group(1)

        print(
            "Weekly sold raw:",
            weekly_sold_raw
        )

    finally:

        browser.close()