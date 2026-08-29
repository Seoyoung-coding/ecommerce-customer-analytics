from playwright.sync_api import sync_playwright
import time


# Weee Korean Store 주소
START_URL = "https://www.weee.com/en/grocery-near-me/asian-supermarket-in-usa/korean-store"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    try:
        # 새 탭 생성
        page = browser.new_page()

        # Korean Store 접속
        page.goto(START_URL)

        print(page.title())


        # 페이지 아래까지 스크롤
        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        # 추가 콘텐츠가 로딩될 시간을 기다린다.
        time.sleep(3)


        # href 안에 "/en/product/"가 포함된 모든 링크를 찾는다.
        product_links = page.locator(
            'a[href*="/en/product/"]'
        )

        # HTML 상의 링크 개수
        print(
            "Product link count:",
            product_links.count()
        )


        # 각 <a> 태그의 실제 URL만 가져온다.
        hrefs = product_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        )


        # set() → 중복 제거
        # sorted() → 실행할 때마다 순서를 일정하게 유지
        unique_hrefs = sorted(
            set(hrefs)
        )


        # 실제 고유 상품 URL 개수
        print(
            "Unique product count:",
            len(unique_hrefs)
        )

    finally:
        browser.close()