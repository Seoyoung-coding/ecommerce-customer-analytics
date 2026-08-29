from playwright.sync_api import sync_playwright
import time
import re


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
        # 여러 상품 수집 테스트
        # ---------------------------------

        # 각 상품의 dictionary 결과를 저장할 리스트
        products = []

        # 처음에는 전체 60개가 아니라
        # 앞의 5개 상품만 테스트한다.
        for product_url in unique_hrefs[:5]:

            try:

                # 상품 URL 하나를 extract_product 함수에 전달한다.
                product = extract_product(
                    page,
                    product_url
                )

                # 추출한 상품 dictionary를
                # products 리스트에 추가한다.
                products.append(product)

                # 현재 어떤 상품까지 수집했는지 확인한다.
                print(
                    "Collected:",
                    product["product_name"]
                )


            # 특정 상품 하나에서 오류가 발생해도
            # 전체 프로그램이 중단되지 않도록 한다.
            except Exception as e:

                print(
                    "Failed:",
                    product_url
                )

                print(
                    "Error:",
                    e
                )

        # 최종적으로 몇 개 상품을 수집했는지 출력
        print(
            "Collected product count:",
            len(products)
        )

        # 수집된 결과 확인
        for product in products:
            print(product)


    finally:

        browser.close()