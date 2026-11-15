
BEGIN;

-- =========================================
-- 1. DIMENSION TABLES
-- =========================================

CREATE TABLE dim_branches (
    branch_id       VARCHAR(20) PRIMARY KEY,
    branch_name     VARCHAR(100) NOT NULL,
    city            VARCHAR(60) NOT NULL,
    region          VARCHAR(60) NOT NULL,
    branch_type     VARCHAR(30) NOT NULL
);


CREATE TABLE dim_suppliers (
    supplier_id         VARCHAR(20) PRIMARY KEY,
    supplier_name       VARCHAR(100) NOT NULL,
    supplier_category   VARCHAR(50) NOT NULL
);


CREATE TABLE dim_date (
    date_id         INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    day             SMALLINT NOT NULL CHECK (day BETWEEN 1 AND 31),
    month           SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name      VARCHAR(15) NOT NULL,
    quarter         VARCHAR(2) NOT NULL,
    year            SMALLINT NOT NULL,
    day_of_week     VARCHAR(15) NOT NULL
);


CREATE TABLE dim_promotions (
    promotion_id    VARCHAR(20) PRIMARY KEY,
    promotion_name  VARCHAR(100) NOT NULL,
    discount_type   VARCHAR(20) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    discount_value  NUMERIC(10,2) NOT NULL,

    CONSTRAINT chk_promotion_discount_type
        CHECK (discount_type IN ('Percentage', 'Fixed Amount')),

    CONSTRAINT chk_promotion_discount_value
        CHECK (
            discount_value > 0
            AND (
                discount_type <> 'Percentage'
                OR discount_value < 100
            )
        ),

    CONSTRAINT chk_promotion_dates
        CHECK (end_date >= start_date)
);


CREATE TABLE dim_products (
    product_id      VARCHAR(20) PRIMARY KEY,
    product_name    VARCHAR(100) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    selling_price   NUMERIC(12,2) NOT NULL CHECK (selling_price > 0),
    unit_cost       NUMERIC(12,2) NOT NULL CHECK (unit_cost > 0),
    supplier_id     VARCHAR(20) NOT NULL,

    CONSTRAINT fk_products_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES dim_suppliers(supplier_id)
);


-- =========================================
-- 2. FACT TABLES
-- =========================================

CREATE TABLE fact_sales (
    sales_line_id   VARCHAR(20) PRIMARY KEY,
    transaction_id  VARCHAR(20) NOT NULL,
    date_id         INTEGER NOT NULL,
    branch_id       VARCHAR(20) NOT NULL,
    product_id      VARCHAR(20) NOT NULL,
    promotion_id    VARCHAR(20),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(12,2) NOT NULL CHECK (unit_price > 0),
    unit_cost       NUMERIC(12,2) NOT NULL CHECK (unit_cost > 0),
    gross_sales     NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT chk_sales_gross
        CHECK (gross_sales = quantity * unit_price),

    CONSTRAINT chk_sales_discount
        CHECK (
            discount_amount >= 0
            AND discount_amount <= gross_sales
        ),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    CONSTRAINT fk_sales_branch
        FOREIGN KEY (branch_id)
        REFERENCES dim_branches(branch_id),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id),

    CONSTRAINT fk_sales_promotion
        FOREIGN KEY (promotion_id)
        REFERENCES dim_promotions(promotion_id)
);


CREATE TABLE fact_returns (
    return_id           VARCHAR(20) PRIMARY KEY,
    sales_line_id       VARCHAR(20) NOT NULL UNIQUE,
    date_id             INTEGER NOT NULL,
    branch_id           VARCHAR(20) NOT NULL,
    product_id          VARCHAR(20) NOT NULL,
    returned_quantity   INTEGER NOT NULL CHECK (returned_quantity > 0),
    refund_amount       NUMERIC(12,2) NOT NULL CHECK (refund_amount >= 0),

    CONSTRAINT fk_returns_sales
        FOREIGN KEY (sales_line_id)
        REFERENCES fact_sales(sales_line_id),

    CONSTRAINT fk_returns_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    CONSTRAINT fk_returns_branch
        FOREIGN KEY (branch_id)
        REFERENCES dim_branches(branch_id),

    CONSTRAINT fk_returns_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id)
);


CREATE TABLE fact_inventory (
    inventory_id        VARCHAR(20) PRIMARY KEY,
    date_id             INTEGER NOT NULL,
    branch_id           VARCHAR(20) NOT NULL,
    product_id          VARCHAR(20) NOT NULL,
    quantity_on_hand    INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_level       INTEGER NOT NULL CHECK (reorder_level > 0),

    CONSTRAINT uq_inventory_snapshot
        UNIQUE (date_id, branch_id, product_id),

    CONSTRAINT fk_inventory_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    CONSTRAINT fk_inventory_branch
        FOREIGN KEY (branch_id)
        REFERENCES dim_branches(branch_id),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES dim_products(product_id)
);

COMMIT;
