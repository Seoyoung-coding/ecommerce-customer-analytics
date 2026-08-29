from playwright.sync_api import sync_playwright
import time


START_URL = "https://www.weee.com/en/grocery-near-me/asian-supermarket-in-usa/korean-store"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    try:
        page = browser.new_page()

        # Weee Korean Store 접속
        page.goto(START_URL)

        print(page.title())


        # 페이지 아래까지 스크롤
        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        time.sleep(3)


        # 상품 링크 탐색
        product_links = page.locator(
            'a[href*="/en/product/"]'
        )

        print(
            "Product link count:",
            product_links.count()
        )


        # URL 추출
        hrefs = product_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        )


        # 중복 제거
        unique_hrefs = sorted(
            set(hrefs)
        )

        print(
            "Unique product count:",
            len(unique_hrefs)
        )


        # 첫 번째 상품 URL 선택
        first_product_url = unique_hrefs[0]

        print(
            "First product URL:",
            first_product_url
        )


        # 첫 번째 상품의 상세페이지로 이동
        page.goto(first_product_url)


        # 상세페이지에 정상적으로 접속했는지 확인
        print(
            "Product page title:",
            page.title()
        )

    finally:
        browser.close()