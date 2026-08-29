# Playwright의 동기식(sync) API를 가져온다.
from playwright.sync_api import sync_playwright

# 프로그램을 잠시 멈출 때 사용한다.
import time

# 문자열 패턴 검색을 위해 정규표현식 모듈을 가져온다.
import re


# 크롤링을 시작할 Weee Korean Store 페이지 주소
START_URL = "https://www.weee.com/en/grocery-near-me/asian-supermarket-in-usa/korean-store"


# Playwright 시작
with sync_playwright() as p:

    # Chromium 브라우저 실행
    # headless=False → 실제 브라우저 창을 화면에 보여준다.
    browser = p.chromium.launch(headless=False)

    try:
        # 새 브라우저 탭 생성
        page = browser.new_page()

        # Weee Korean Store 페이지로 이동
        page.goto(START_URL)

        # 페이지 정상 접속 확인
        print(page.title())


        # ---------------------------------
        # 1. 상품 URL 수집
        # ---------------------------------

        # 페이지의 가장 아래까지 스크롤한다.
        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight)"
        )

        # 추가 콘텐츠가 로딩될 시간을 준다.
        time.sleep(3)

        # href 안에 "/en/product/"가 포함된 모든 링크를 찾는다.
        product_links = page.locator(
            'a[href*="/en/product/"]'
        )

        # HTML 상의 상품 링크 개수 출력
        print(
            "Product link count:",
            product_links.count()
        )

        # 각 <a> 태그에서 실제 href URL만 가져온다.
        hrefs = product_links.evaluate_all(
            "elements => elements.map(element => element.href)"
        )

        # 중복 URL 제거 + 정렬
        unique_hrefs = sorted(
            set(hrefs)
        )

        # 실제 고유 상품 URL 개수 출력
        print(
            "Unique product count:",
            len(unique_hrefs)
        )


        # ---------------------------------
        # 2. 첫 번째 상품 상세페이지 접속
        # ---------------------------------

        # 테스트용으로 첫 번째 상품 URL 선택
        first_product_url = unique_hrefs[0]

        print(
            "First product URL:",
            first_product_url
        )

        # 첫 번째 상품 상세페이지로 이동
        page.goto(first_product_url)

        # 상세페이지 정상 접속 확인
        print(
            "Product page title:",
            page.title()
        )


        # ---------------------------------
        # 3. 상품명 raw 추출
        # ---------------------------------

        # 상품명 HTML 요소를 data-testid로 찾는다.
        product_name_element = page.get_by_test_id(
            "wid-pdp-product-name"
        )

        # 상품명 텍스트 추출
        product_name = product_name_element.inner_text()

        print(
            "Product name:",
            product_name
        )


        # ---------------------------------
        # 4. 가격 raw 추출
        # ---------------------------------

        # 가격 정보를 가진 HTML 요소들을 찾는다.
        price_elements = page.get_by_test_id(
            "wid-pdp-price-left-part"
        )

        # 모든 가격 후보 텍스트 가져오기
        price_texts = price_elements.all_inner_texts()

        # 아직 가격을 찾지 못했으므로 None으로 시작
        raw_price_text = None

        # 가격 후보들을 하나씩 확인한다.
        for text in price_texts:

            # 빈 문자열이 아니면 실제 가격 후보로 사용
            if text.strip():

                raw_price_text = text.strip()

                # 필요한 값을 찾았으므로 반복 종료
                break

        print(
            "Raw price text:",
            raw_price_text
        )


        # ---------------------------------
        # 5. 브랜드 raw 추출
        # ---------------------------------

        # 브랜드 링크 요소 찾기
        brand_elements = page.get_by_test_id(
            "wid-pdp-brand-link"
        )

        # 브랜드 정보가 존재할 수도 있고 없을 수도 있으므로
        # 개수를 먼저 확인한다.
        if brand_elements.count() > 0:

            # 첫 번째 브랜드 요소 선택
            brand_element = brand_elements.first

            # 원본 브랜드 텍스트 추출
            brand_raw = brand_element.inner_text()

        else:
            # 브랜드 정보가 없으면 None
            brand_raw = None

        print(
            "Brand raw:",
            brand_raw
        )


        # ---------------------------------
        # 6. 원산지 raw 추출
        # ---------------------------------

        # 같은 상품 URL을 HTTP 요청으로 다시 받아
        # 서버가 내려주는 원본 HTML을 가져온다.
        response = page.request.get(
            first_product_url
        )

        # HTTP 응답 내용을 문자열로 가져온다.
        raw_html = response.text()

        # raw HTML 안에서
        # property_key가 origin인 항목의
        # property_value 값을 찾는다.
        origin_match = re.search(
            r'\\"property_key\\":\\"origin\\".*?'
            r'\\"property_value\\":\\"([^"]+)\\"',
            raw_html
        )

        # 아직 원산지를 찾지 못했다고 가정
        origin_raw = None

        # 정규표현식이 일치했다면
        if origin_match:

            # 첫 번째 캡처 그룹의 값 추출
            # 예: South Korea
            origin_raw = origin_match.group(1)

        print(
            "Origin raw:",
            origin_raw
        )

        # ---------------------------------
        # 7. 상품 평점 raw 추출
        # ---------------------------------

        # raw HTML 안에서
        # "overall_rating":"값"
        # 형태를 찾는다.
        rating_match = re.search(
            r'\\"overall_rating\\":\\"([^"]*)\\"',
            raw_html
        )

        # 기본값은 None
        rating_raw = None

        # overall_rating 값이 존재하면
        if rating_match:
            # 괄호 안에서 잡힌 실제 평점 값만 가져온다.
            # 예: "5.0" -> 5.0
            rating_raw = rating_match.group(1)

        # 아직 숫자형으로 변환하지 않고
        # raw 문자열 그대로 출력한다.
        print(
            "Rating raw:",
            rating_raw
        )

    finally:
        # 중간에 에러가 발생하더라도
        # Chromium 브라우저는 반드시 종료된다.
        browser.close()