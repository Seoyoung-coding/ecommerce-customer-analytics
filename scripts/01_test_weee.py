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
        # 7. 카테고리 raw 추출
        # ---------------------------------

        category_match = re.search(
            r'\\"category_name\\":\\"([^"]*)\\"',
            raw_html
        )

        category_raw = None

        if category_match:
            category_raw = category_match.group(1)

        print(
            "Category raw:",
            category_raw
        )

        # ---------------------------------
        # 8. 상위 카테고리 raw 추출
        # ---------------------------------

        parent_category_match = re.search(
            r'\\"parent_category_name\\":\\"([^"]*)\\"',
            raw_html
        )

        parent_category_raw = None

        if parent_category_match:
            parent_category_raw = parent_category_match.group(1)

        print(
            "Parent category raw:",
            parent_category_raw
        )

        # ---------------------------------
        # 9. 상품 용량 raw 추출
        # ---------------------------------

        unit_match = re.search(
            r'\\"unit_info\\":\\"([^"]*)\\"',
            raw_html
        )

        unit_raw = None

        if unit_match:
            unit_raw = unit_match.group(1)

        print(
            "Unit raw:",
            unit_raw
        )

        # ---------------------------------
        # 10. 상품 판매량 raw 추출
        # ---------------------------------

        sold_count_match = re.search(
            r'\\"sold_count\\":(?:\\"([^"]*)\\"|(\d+)|null)',
            raw_html
        )

        sold_count_raw = None

        if sold_count_match:

            if sold_count_match.group(1):
                sold_count_raw = sold_count_match.group(1)

            elif sold_count_match.group(2):
                sold_count_raw = sold_count_match.group(2)

        print(
            "Sold count raw:",
            sold_count_raw
        )

        # ---------------------------------
        # 11. 최근 판매량 표시 raw 추출
        # ---------------------------------

        last_week_sold_match = re.search(
            r'\\"last_week_sold_count_ui\\":(?:\\"([^"]*)\\"|(\d+)|null)',
            raw_html
        )

        last_week_sold_raw = None

        if last_week_sold_match:

            if last_week_sold_match.group(1):
                last_week_sold_raw = last_week_sold_match.group(1)

            elif last_week_sold_match.group(2):
                last_week_sold_raw = last_week_sold_match.group(2)

        print(
            "Last week sold raw:",
            last_week_sold_raw
        )

        # ---------------------------------
        # 10. 상품 판매 데이터 영역 찾기
        # ---------------------------------

        # product_properties가 시작되는 위치를 찾는다.
        # 이 주변은 실제 "상품 객체" 데이터가 있는 영역이다.
        product_data_start = raw_html.find(
            '\\"product_properties\\"'
        )

        # 상품 객체 뒤에 등장하는 vendor 정보의 시작 위치를 찾는다.
        product_data_end = raw_html.find(
            '\\"vender_info_view\\"',
            product_data_start
        )

        # 상품 객체 시작 위치를 찾았다면
        if product_data_start != -1:

            # vendor 정보 위치도 찾았다면
            if product_data_end != -1:

                # 실제 상품 데이터 영역만 잘라낸다.
                product_data_block = raw_html[
                                     product_data_start:product_data_end
                                     ]

            else:

                # vendor 위치를 못 찾은 경우를 대비해서
                # product_properties 뒤 5000글자까지만 가져온다.
                product_data_block = raw_html[
                                     product_data_start:product_data_start + 5000
                                     ]

        else:

            # 상품 데이터 영역을 찾지 못하면 빈 문자열
            product_data_block = ""

        # ---------------------------------
        # 11. sold_count raw 추출
        # ---------------------------------

        # 이제 raw_html 전체가 아니라
        # 실제 상품 데이터 영역 안에서만 sold_count를 찾는다.
        sold_count_match = re.search(
            r'\\"sold_count\\":(?:\\"([^"]*)\\"|(\d+)|null)',
            product_data_block
        )

        sold_count_raw = None

        if sold_count_match:

            # 문자열 값이 있으면 사용
            if sold_count_match.group(1):
                sold_count_raw = sold_count_match.group(1)

            # 숫자 값이 있으면 사용
            elif sold_count_match.group(2):
                sold_count_raw = sold_count_match.group(2)

        print(
            "Sold count raw:",
            sold_count_raw
        )

        # ---------------------------------
        # 12. 지난주 판매량 raw 추출
        # ---------------------------------

        last_week_sold_match = re.search(
            r'\\"last_week_sold_count_ui\\":(?:\\"([^"]*)\\"|(\d+)|null)',
            product_data_block
        )

        last_week_sold_raw = None

        if last_week_sold_match:

            if last_week_sold_match.group(1):
                last_week_sold_raw = last_week_sold_match.group(1)

            elif last_week_sold_match.group(2):
                last_week_sold_raw = last_week_sold_match.group(2)

        print(
            "Last week sold raw:",
            last_week_sold_raw
        )

    finally:
        # 중간에 에러가 발생하더라도
        # Chromium 브라우저는 반드시 종료된다.
        browser.close()