-- 이 프로젝트에서 사용할 데이터베이스를 선택한다.
USE ecommerce_analytics;


-- Weee에서 웹스크래핑한 원본 데이터를 저장할 테이블을 만든다.
CREATE TABLE raw_weee_products (

    -- 각 row를 구분하기 위한 고유 번호
    -- AUTO_INCREMENT이므로 1, 2, 3 ... 자동 생성된다.
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    -- 데이터를 가져온 쇼핑몰
    -- 현재는 WEEE지만 나중에 AMAZON, TARGET 등이 추가될 수 있다.
    retailer VARCHAR(50),

    -- 이 상품 정보를 언제 수집했는지 저장한다.
    observed_at DATE,

    -- Weee 상품 상세페이지 URL
    product_url TEXT,

    -- 웹페이지에서 가져온 상품명 원본
    product_name TEXT,

    -- 가격 원본
    -- 예: "$\n13\n49\n$0.85/oz"
    price_raw TEXT,

    -- 브랜드 원본
    -- 예: "Shop more from Binggrae"
    brand_raw TEXT,

    -- 원산지 원본
    -- 예: "South Korea"
    origin_raw VARCHAR(100),

    -- 세부 카테고리 원본
    -- 예: "Meals \\u0026 Entrees"
    category_raw VARCHAR(255),

    -- 상위 카테고리 원본
    -- 예: "Frozen", "Beverages", "Personal care"
    parent_category_raw VARCHAR(255),

    -- 상품 용량 원본
    -- 예: "450 g", "200 ml"
    unit_raw VARCHAR(100),

    -- 상품 판매량 원본
    sold_count_raw VARCHAR(100),

    -- 최근 판매량 원본
    last_week_sold_raw VARCHAR(100)

);
