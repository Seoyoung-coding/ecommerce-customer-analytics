from datetime import date
import re
import time
from playwright.sync_api import sync_playwright



START_URL = "https://www.weee.com/en/grocery-near-me/asian-supermarket-in-usa/korean-store"


# --------------------------------------------------
# 상품 1개의 상세정보를 추출하는 함수
# --------------------------------------------------
def extract_product(page, product_url):

    # 상품 상세페이지로 이동
    page.goto(product_url)

    # ---------------------------------
    # 상품명
    # ---------------------------------

    product_name_element = page.get_by_test_id(
        "wid-pdp-product-name"
    )

    product_name = product_name_element.inner_text()


    # ---------------------------------
    # 가격 raw
    # ---------------------------------

    price_elements = page.get_by_test_id(
        "wid-pdp-price-left-part"
    )

    price_texts = price_elements.all_inner_texts()

    raw_price_text = None

    for text in price_texts:

        if text.strip():

            raw_price_text = text.strip()

            break


    # ---------------------------------
    # 브랜드 raw
    # ---------------------------------

    brand_elements = page.get_by_test_id(
        "wid-pdp-brand-link"
    )

    brand_raw = None

    if brand_elements.count() > 0:

        brand_raw = brand_elements.first.inner_text()


    # ---------------------------------
    # 서버 원본 HTML 가져오기
    # ---------------------------------

    response = page.request.get(product_url)

    raw_html = response.text()


    # ---------------------------------
    # 원산지 raw
    # ---------------------------------

    origin_match = re.search(
        r'\\"property_key\\":\\"origin\\".*?'
        r'\\"property_value\\":\\"([^"]+)\\"',
        raw_html
    )

    origin_raw = None

    if origin_match:

        origin_raw = origin_match.group(1)


    # ---------------------------------
    # 카테고리 raw
    # ---------------------------------

    category_match = re.search(
        r'\\"category_name\\":\\"([^"]*)\\"',
        raw_html
    )

    category_raw = None

    if category_match:

        category_raw = category_match.group(1)


    # ---------------------------------
    # 상위 카테고리 raw
    # ---------------------------------

    parent_category_match = re.search(
        r'\\"parent_category_name\\":\\"([^"]*)\\"',
        raw_html
    )

    parent_category_raw = None

    if parent_category_match:

        parent_category_raw = parent_category_match.group(1)


    # ---------------------------------
    # 용량 raw
    # ---------------------------------

    unit_match = re.search(
        r'\\"unit_info\\":\\"([^"]*)\\"',
        raw_html
    )

    unit_raw = None

    if unit_match:

        unit_raw = unit_match.group(1)


    # ---------------------------------
    # 실제 상품 데이터 영역만 자르기
    # ---------------------------------

    product_data_start = raw_html.find(
        '\\"product_properties\\"'
    )

    product_data_end = raw_html.find(
        '\\"vender_info_view\\"',
        product_data_start
    )

    if product_data_start != -1:

        if product_data_end != -1:

            product_data_block = raw_html[
                product_data_start:product_data_end
            ]

        else:

            product_data_block = raw_html[
                product_data_start:product_data_start + 5000
            ]

    else:

        product_data_block = ""


    # ---------------------------------
    # sold_count raw
    # ---------------------------------

    sold_count_match = re.search(
        r'\\"sold_count\\":(?:\\"([^"]*)\\"|(\d+)|null)',
        product_data_block
    )

    sold_count_raw = None

    if sold_count_match:

        if sold_count_match.group(1):

            sold_count_raw = sold_count_match.group(1)

        elif sold_count_match.group(2):

            sold_count_raw = sold_count_match.group(2)


    # ---------------------------------
    # last_week_sold_count raw
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


    # ---------------------------------
    # 상품 하나의 결과를 dictionary로 반환
    # ---------------------------------

    return {
        "product_url": product_url,
        "product_name": product_name,
        "price_raw": raw_price_text,
        "brand_raw": brand_raw,
        "origin_raw": origin_raw,
        "category_raw": category_raw,
        "parent_category_raw": parent_category_raw,
        "unit_raw": unit_raw,
        "sold_count_raw": sold_count_raw,
        "last_week_sold_raw": last_week_sold_raw
    }


# --------------------------------------------------
# 메인 실행 부분
# --------------------------------------------------

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


        # 상품 링크 찾기
        product_links = page.locator(
            'a[href*="/en/product/"]'
        )


        print(
            "Product link count:",
            product_links.count()
        )


        # 실제 URL만 추출
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

        # ---------------------------------
        # 60개 상품 전체 수집
        # ---------------------------------

        # 각 상품의 dictionary를 저장할 리스트
        products = []

        # unique_hrefs에 들어있는 모든 상품 URL을 하나씩 처리한다.
        #
        # enumerate(..., start=1)
        # → 상품의 순번도 함께 가져온다.
        #
        # 예:
        # 1, 첫 번째 URL
        # 2, 두 번째 URL
        # ...
        for index, product_url in enumerate(unique_hrefs, start=1):

            try:

                # 현재 상품 상세정보를 추출한다.
                product = extract_product(
                    page,
                    product_url
                )

                # 추출한 dictionary를 products 리스트에 저장한다.
                products.append(product)

                # 진행 상황을 출력한다.
                print(
                    f"[{index}/{len(unique_hrefs)}] Collected:",
                    product["product_name"]
                )

                # Weee 서버에 너무 빠르게 요청하지 않도록
                # 각 상품 수집 후 1초 기다린다.
                time.sleep(1)


            # 특정 상품 하나에서 오류가 발생해도
            # 나머지 상품 수집은 계속한다.
            except Exception as e:

                print(
                    f"[{index}/{len(unique_hrefs)}] Failed:",
                    product_url
                )

                print(
                    "Error:",
                    e
                )

        # 전체 작업이 끝난 후
        # 실제 성공적으로 수집된 상품 개수를 출력한다.
        print(
            "Collected product count:",
            len(products)
        )
    finally:

        browser.close()