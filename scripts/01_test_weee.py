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


        # 모든 상품 URL 추출
        hrefs = product_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        )


        # URL 중복 제거
        unique_hrefs = sorted(
            set(hrefs)
        )

        print(
            "Unique product count:",
            len(unique_hrefs)
        )


        # 첫 상품 선택
        first_product_url = unique_hrefs[0]

        print(
            "First product URL:",
            first_product_url
        )


        # 상품 상세페이지 접속
        page.goto(first_product_url)

        print(
            "Product page title:",
            page.title()
        )


        # Weee가 상품명에 부여한 data-testid를 이용하여
        # 상품명 HTML 요소를 정확하게 찾는다.
        product_name_element = page.get_by_test_id(
            "wid-pdp-product-name"
        )


        # HTML 요소 안의 실제 문자열 추출
        product_name = product_name_element.inner_text()


        # raw 상품명 출력
        print(
            "Product name:",
            product_name
        )

    finally:
        browser.close()