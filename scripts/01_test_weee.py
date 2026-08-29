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


        # 중복 URL 제거
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


        # 상품 상세페이지 이동
        page.goto(first_product_url)

        print(
            "Product page title:",
            page.title()
        )


        # -----------------------------
        # 상품명
        # -----------------------------

        product_name_element = page.get_by_test_id(
            "wid-pdp-product-name"
        )

        product_name = product_name_element.inner_text()

        print(
            "Product name:",
            product_name
        )


        # -----------------------------
        # 가격
        # -----------------------------

        # 가격 정보를 담고 있는 HTML 요소를 찾는다.
        price_elements = page.get_by_test_id(
            "wid-pdp-price-left-part"
        )


        # 같은 test id를 가진 요소가 여러 개 있을 수 있으므로
        # 모든 요소의 텍스트를 가져온다.
        price_texts = price_elements.all_inner_texts()


        # 아직 실제 가격을 찾지 못했으므로
        # 초기값은 None으로 둔다.
        raw_price_text = None


        # 가격 후보를 하나씩 검사한다.
        for text in price_texts:

            # 빈 문자열이 아닌 요소를 찾는다.
            if text.strip():

                # 웹페이지에서 보이는 원본 가격 문자열을 저장한다.
                raw_price_text = text.strip()

                # 필요한 값을 찾았으므로 반복 종료
                break


        # 아직 정제하지 않은 raw 가격 출력
        print(
            "Raw price text:",
            raw_price_text
        )

    finally:
        browser.close()