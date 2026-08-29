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


        # ---------------------------------
        # 상품 URL 수집
        # ---------------------------------

        # 상품 상세페이지 링크들을 찾는다.
        product_links = page.locator(
            'a[href*="/en/product/"]'
        )

        print(
            "Product link count:",
            product_links.count()
        )


        # 각 링크의 실제 href 값을 가져온다.
        hrefs = product_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        )


        # 중복 URL 제거 후 정렬
        unique_hrefs = sorted(
            set(hrefs)
        )

        print(
            "Unique product count:",
            len(unique_hrefs)
        )


        # 테스트용으로 첫 상품을 선택
        first_product_url = unique_hrefs[0]

        print(
            "First product URL:",
            first_product_url
        )


        # ---------------------------------
        # 상품 상세페이지 접속
        # ---------------------------------

        page.goto(first_product_url)

        print(
            "Product page title:",
            page.title()
        )


        # ---------------------------------
        # 상품명 raw 추출
        # ---------------------------------

        product_name_element = page.get_by_test_id(
            "wid-pdp-product-name"
        )

        product_name = product_name_element.inner_text()

        print(
            "Product name:",
            product_name
        )


        # ---------------------------------
        # 가격 raw 추출
        # ---------------------------------

        # 가격 관련 HTML 요소들을 찾는다.
        price_elements = page.get_by_test_id(
            "wid-pdp-price-left-part"
        )


        # 모든 가격 후보 텍스트를 가져온다.
        price_texts = price_elements.all_inner_texts()


        raw_price_text = None


        # 빈 요소를 제외하고 실제 가격 문자열 선택
        for text in price_texts:

            if text.strip():

                raw_price_text = text.strip()

                break


        print(
            "Raw price text:",
            raw_price_text
        )


        # ---------------------------------
        # 브랜드 raw 추출
        # ---------------------------------

        # Weee에서 브랜드 링크에 부여한
        # data-testid를 이용해 브랜드 요소를 찾는다.
        brand_element = page.get_by_test_id(
            "wid-pdp-brand-link"
        ).first


        # 브랜드 영역의 원본 텍스트를 그대로 가져온다.
        brand_raw = brand_element.inner_text()


        # 아직 "Shop more from ..." 문구를 제거하지 않는다.
        # 나중 SQL cleaning 단계에서 처리할 예정이다.
        print(
            "Brand raw:",
            brand_raw
        )

    finally:
        browser.close()