/*
============================================================
PROJECT: 6M MART
TITLE: Retail Intelligence & Performance Analytics
DATABASE: sixm_mart
PERIOD: January 2024 - December 2025
CURRENCY: PHP

PURPOSE:
Analyze sales performance, branch performance, product
profitability, promotional effectiveness, inventory
availability, returns, and business opportunities.

DATA DISCLAIMER:
All records in this project are synthetic and generated
for portfolio and demonstration purposes.

============================================================
*/


/*
============================================================
SECTION 1: OVERALL BUSINESS PERFORMANCE
============================================================

Objectives:
- Calculate gross sales and net sales
- Calculate total discounts and refunds
- Determine total orders and units sold
- Calculate COGS, gross profit, and gross profit margin
- Calculate the overall return rate

*/

/*
------------------------------------------------------------
QUERY 1.1: OVERALL BUSINESS PERFORMANCE
------------------------------------------------------------

Purpose:
Calculate the key financial and operational KPIs across
the entire business for 2024-2025.

Metrics:
- Gross Sales
- Discounts
- Refunds
- Net Sales
- Total Orders
- Units Sold
- Average Order Value
- Cost of Goods Sold
- Gross Profit
- Gross Profit Margin
- Return Rate

Methodology:
Returns are aggregated by sales line before joining to
fact_sales to prevent duplicate sales records.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
)

SELECT

    -- Sales metrics
    ROUND(SUM(s.gross_sales), 2) AS gross_sales,

    ROUND(SUM(s.discount_amount), 2) AS total_discounts,

    ROUND(
        SUM(COALESCE(r.refund_amount, 0)),
        2
    ) AS total_refunds,

    ROUND(
        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ),
        2
    ) AS net_sales,

    -- Operational metrics
    COUNT(DISTINCT s.transaction_id) AS total_orders,

    SUM(
        s.quantity - COALESCE(r.returned_quantity, 0)
    ) AS net_units_sold,

    ROUND(
        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        )
        / NULLIF(COUNT(DISTINCT s.transaction_id), 0),
        2
    ) AS average_order_value,

    -- Profitability metrics
    ROUND(
        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ),
        2
    ) AS total_cogs,

    ROUND(
        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        )
        -
        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ),
        2
    ) AS gross_profit,

    ROUND(
        100.0 *
        (
            SUM(
                s.gross_sales
                - s.discount_amount
                - COALESCE(r.refund_amount, 0)
            )
            -
            SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            )
        )
        /
        NULLIF(
            SUM(
                s.gross_sales
                - s.discount_amount
                - COALESCE(r.refund_amount, 0)
            ),
            0
        ),
        2
    ) AS gross_profit_margin_pct,

    -- Returns metric
    ROUND(
        100.0 *
        SUM(COALESCE(r.returned_quantity, 0))
        / NULLIF(SUM(s.quantity), 0),
        2
    ) AS return_rate_pct

FROM fact_sales s

LEFT JOIN returns_by_line r
    ON s.sales_line_id = r.sales_line_id;

/*
============================================================
SECTION 2: MONTHLY AND YEARLY SALES PERFORMANCE
============================================================

Objectives:
- Analyze monthly net sales
- Calculate month-over-month growth
- Compare annual sales performance
- Identify seasonal sales patterns

*/

/*
------------------------------------------------------------
QUERY 2.1: MONTHLY SALES PERFORMANCE
------------------------------------------------------------

Purpose:
Analyze monthly sales trends and calculate month-over-month
growth in net sales.

Metrics:
- Monthly Net Sales
- Total Orders
- Month-over-Month Growth (%)

Methodology:
Returns are aggregated by sales line before joining to
fact_sales.

LAG() retrieves the previous month's net sales.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

monthly_sales AS (
    SELECT
        d.year,
        d.month,
        d.month_name,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        COUNT(DISTINCT s.transaction_id) AS total_orders

    FROM fact_sales s

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        d.year,
        d.month,
        d.month_name
),

sales_with_previous_month AS (
    SELECT
        *,
        LAG(net_sales) OVER (
            ORDER BY year, month
        ) AS previous_month_sales

    FROM monthly_sales
)

SELECT
    year,
    month,
    month_name,

    ROUND(net_sales, 2) AS net_sales,

    total_orders,

    ROUND(
        100.0 * (net_sales - previous_month_sales)
        / NULLIF(previous_month_sales, 0),
        2
    ) AS mom_growth_pct

FROM sales_with_previous_month

ORDER BY
    year,
    month;

/*
------------------------------------------------------------
QUERY 2.2: ANNUAL SALES PERFORMANCE
------------------------------------------------------------

Purpose:
Compare annual net sales and calculate year-over-year
growth.

Metrics:
- Annual Net Sales
- Total Orders
- Year-over-Year Growth (%)

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

annual_sales AS (
    SELECT
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        COUNT(DISTINCT s.transaction_id) AS total_orders

    FROM fact_sales s

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY d.year
),

sales_with_previous_year AS (
    SELECT
        *,
        LAG(net_sales) OVER (
            ORDER BY year
        ) AS previous_year_sales

    FROM annual_sales
)

SELECT
    year,

    ROUND(net_sales, 2) AS net_sales,

    total_orders,

    ROUND(
        net_sales - previous_year_sales,
        2
    ) AS sales_difference,

    ROUND(
        100.0 * (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS yoy_growth_pct

FROM sales_with_previous_year

ORDER BY year;

/*
============================================================
SECTION 3: BRANCH PERFORMANCE
============================================================

Objectives:
- Compare branch revenue and profitability
- Analyze year-over-year branch performance
- Identify growing and declining branches
- Compare order growth and average order value

*/

/*
------------------------------------------------------------
QUERY 3.1: OVERALL BRANCH PERFORMANCE
------------------------------------------------------------

Purpose:
Compare financial and operational performance across
all 8 supermarket branches.

Metrics:
- Net Sales
- Total Orders
- COGS
- Gross Profit
- Gross Profit Margin
- Return Rate

Methodology:
Returns are aggregated by sales line before joining
to sales to prevent duplicate records.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
)

SELECT
    b.branch_name,

    -- Sales metrics
    ROUND(
        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ),
        2
    ) AS net_sales,

    COUNT(DISTINCT s.transaction_id) AS total_orders,

    -- Profitability metrics
    ROUND(
        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ),
        2
    ) AS total_cogs,

    ROUND(
        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        )
        -
        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ),
        2
    ) AS gross_profit,

    ROUND(
        100.0 * (
            SUM(
                s.gross_sales
                - s.discount_amount
                - COALESCE(r.refund_amount, 0)
            )
            -
            SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            )
        )
        /
        NULLIF(
            SUM(
                s.gross_sales
                - s.discount_amount
                - COALESCE(r.refund_amount, 0)
            ),
            0
        ),
        2
    ) AS gross_profit_margin_pct,

    -- Return rate
    ROUND(
        100.0 * SUM(COALESCE(r.returned_quantity, 0))
        / NULLIF(SUM(s.quantity), 0),
        2
    ) AS return_rate_pct

FROM fact_sales s

JOIN dim_branches b
    ON s.branch_id = b.branch_id

LEFT JOIN returns_by_line r
    ON s.sales_line_id = r.sales_line_id

GROUP BY b.branch_name

ORDER BY net_sales DESC;

/*
------------------------------------------------------------
QUERY 3.2: BRANCH YEAR-OVER-YEAR PERFORMANCE
------------------------------------------------------------

Purpose:
Compare annual net sales across branches to identify
growth and decline.

Metrics:
- 2024 Net Sales
- 2025 Net Sales
- Sales Difference
- Year-over-Year Growth (%)

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

branch_annual_sales AS (
    SELECT
        b.branch_name,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales

    FROM fact_sales s

    JOIN dim_branches b
        ON s.branch_id = b.branch_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        b.branch_name,
        d.year
),

branch_comparison AS (
    SELECT
        branch_name,
        year,
        net_sales,

        LAG(net_sales) OVER (
            PARTITION BY branch_name
            ORDER BY year
        ) AS previous_year_sales

    FROM branch_annual_sales
)

SELECT
    branch_name,
    year,

    ROUND(net_sales, 2) AS net_sales,

    ROUND(
        net_sales - previous_year_sales,
        2
    ) AS sales_difference,

    ROUND(
        100.0 * (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS yoy_growth_pct

FROM branch_comparison

WHERE year = 2025

ORDER BY yoy_growth_pct DESC;

/*
------------------------------------------------------------
QUERY 3.3: BRANCH ORDER GROWTH VS. SALES GROWTH
------------------------------------------------------------

Purpose:
Compare changes in transaction volume against changes
in net sales across branches.

Metrics:
- 2024 Orders
- 2025 Orders
- Order Growth (%)
- 2024 Net Sales
- 2025 Net Sales
- Sales Growth (%)

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

branch_yearly_performance AS (
    SELECT
        b.branch_name,
        d.year,

        COUNT(DISTINCT s.transaction_id) AS total_orders,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales

    FROM fact_sales s

    JOIN dim_branches b
        ON s.branch_id = b.branch_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        b.branch_name,
        d.year
),

branch_comparison AS (
    SELECT
        branch_name,
        year,
        total_orders,
        net_sales,

        LAG(total_orders) OVER (
            PARTITION BY branch_name
            ORDER BY year
        ) AS previous_year_orders,

        LAG(net_sales) OVER (
            PARTITION BY branch_name
            ORDER BY year
        ) AS previous_year_sales

    FROM branch_yearly_performance
)

SELECT
    branch_name,

    MAX(previous_year_orders) AS orders_2024,

    MAX(total_orders) AS orders_2025,

    ROUND(
        100.0 * (
            MAX(total_orders) - MAX(previous_year_orders)
        )
        / NULLIF(MAX(previous_year_orders), 0),
        2
    ) AS order_growth_pct,

    ROUND(
        100.0 * (
            MAX(net_sales) - MAX(previous_year_sales)
        )
        / NULLIF(MAX(previous_year_sales), 0),
        2
    ) AS sales_growth_pct

FROM branch_comparison

WHERE year = 2025

GROUP BY branch_name

ORDER BY order_growth_pct DESC;

/*
------------------------------------------------------------
QUERY 3.4: AVERAGE ORDER VALUE BY BRANCH AND YEAR
------------------------------------------------------------

Purpose:
Compare average customer spending per transaction
across branches and years.

Metrics:
- 2024 Average Order Value
- 2025 Average Order Value
- AOV Change (%)

Formula:
AOV = Net Sales / Total Orders

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

branch_yearly_sales AS (
    SELECT
        b.branch_name,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        COUNT(DISTINCT s.transaction_id) AS total_orders

    FROM fact_sales s

    JOIN dim_branches b
        ON s.branch_id = b.branch_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        b.branch_name,
        d.year
),

branch_aov AS (
    SELECT
        branch_name,
        year,

        net_sales / NULLIF(total_orders, 0) AS average_order_value

    FROM branch_yearly_sales
),

aov_comparison AS (
    SELECT
        branch_name,
        year,
        average_order_value,

        LAG(average_order_value) OVER (
            PARTITION BY branch_name
            ORDER BY year
        ) AS previous_year_aov

    FROM branch_aov
)

SELECT
    branch_name,

    ROUND(previous_year_aov, 2) AS aov_2024,

    ROUND(average_order_value, 2) AS aov_2025,

    ROUND(
        100.0 * (
            average_order_value - previous_year_aov
        ) / NULLIF(previous_year_aov, 0),
        2
    ) AS aov_change_pct

FROM aov_comparison

WHERE year = 2025

ORDER BY aov_change_pct DESC;

/*
============================================================
SECTION 4: PRODUCT AND CATEGORY PERFORMANCE
============================================================

Objectives:
- Identify top-performing products
- Compare product category performance
- Analyze sales and profit growth
- Identify declining products

*/

/*
------------------------------------------------------------
QUERY 4.1: TOP 10 PRODUCTS BY NET SALES
------------------------------------------------------------

Purpose:
Identify the highest-revenue products and evaluate
their profitability.

Metrics:
- Net Sales
- Net Units Sold
- COGS
- Gross Profit
- Gross Profit Margin

Ranking:
Top 10 products based on net sales.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_performance AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            s.quantity - COALESCE(r.returned_quantity, 0)
        ) AS net_units_sold,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS total_cogs

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        p.product_id,
        p.product_name,
        p.category
)

SELECT
    product_name,
    category,

    ROUND(net_sales, 2) AS net_sales,

    net_units_sold,

    ROUND(total_cogs, 2) AS total_cogs,

    ROUND(net_sales - total_cogs, 2) AS gross_profit,

    ROUND(
        100.0 * (net_sales - total_cogs)
        / NULLIF(net_sales, 0),
        2
    ) AS gross_profit_margin_pct

FROM product_performance

ORDER BY net_sales DESC

LIMIT 10;

/*
------------------------------------------------------------
QUERY 4.2: CATEGORY PERFORMANCE
------------------------------------------------------------

Purpose:
Evaluate revenue contribution and profitability
across the six product categories.

Metrics:
- Product Count
- Net Sales
- Revenue Contribution (%)
- Net Units Sold
- COGS
- Gross Profit
- Gross Profit Margin

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

category_performance AS (
    SELECT
        p.category,

        COUNT(DISTINCT p.product_id) AS product_count,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            s.quantity - COALESCE(r.returned_quantity, 0)
        ) AS net_units_sold,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS total_cogs

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY p.category
)

SELECT
    category,

    product_count,

    ROUND(net_sales, 2) AS net_sales,

    ROUND(
        100.0 * net_sales
        / NULLIF(SUM(net_sales) OVER (), 0),
        2
    ) AS sales_contribution_pct,

    net_units_sold,

    ROUND(total_cogs, 2) AS total_cogs,

    ROUND(net_sales - total_cogs, 2) AS gross_profit,

    ROUND(
        100.0 * (net_sales - total_cogs)
        / NULLIF(net_sales, 0),
        2
    ) AS gross_profit_margin_pct

FROM category_performance

ORDER BY net_sales DESC;


/*
------------------------------------------------------------
QUERY 4.3: PRODUCT YEAR-OVER-YEAR SALES GROWTH
------------------------------------------------------------

Purpose:
Compare product sales between 2024 and 2025 to identify
products with increasing or decreasing demand.

Metrics:
- 2024 Net Sales
- 2025 Net Sales
- Sales Difference
- YoY Growth (%)
- 2024 Net Units
- 2025 Net Units

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_yearly_sales AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            s.quantity - COALESCE(r.returned_quantity, 0)
        ) AS net_units_sold

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,
        year,
        net_sales,
        net_units_sold,

        LAG(net_sales) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_sales,

        LAG(net_units_sold) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_units

    FROM product_yearly_sales
)

SELECT
    product_name,
    category,

    ROUND(previous_year_sales, 2) AS sales_2024,

    ROUND(net_sales, 2) AS sales_2025,

    ROUND(
        net_sales - previous_year_sales,
        2
    ) AS sales_difference,

    ROUND(
        100.0 * (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS sales_growth_pct,

    previous_year_units AS units_2024,

    net_units_sold AS units_2025

FROM product_comparison

WHERE year = 2025

ORDER BY sales_growth_pct DESC;


/*
------------------------------------------------------------
QUERY 4.4: BIGGEST ABSOLUTE PRODUCT SALES INCREASES
------------------------------------------------------------

Purpose:
Identify products contributing the largest peso
increases in net sales from 2024 to 2025.

Metrics:
- 2024 Net Sales
- 2025 Net Sales
- Sales Difference
- YoY Growth (%)

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_yearly_sales AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,
        year,
        net_sales,

        LAG(net_sales) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_sales

    FROM product_yearly_sales
)

SELECT
    product_name,
    category,

    ROUND(previous_year_sales, 2) AS sales_2024,

    ROUND(net_sales, 2) AS sales_2025,

    ROUND(
        net_sales - previous_year_sales,
        2
    ) AS sales_difference,

    ROUND(
        100.0 * (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS sales_growth_pct

FROM product_comparison

WHERE year = 2025

ORDER BY sales_difference DESC

LIMIT 15;


/*
------------------------------------------------------------
QUERY 4.5: BIGGEST ABSOLUTE PRODUCT SALES DECLINES
------------------------------------------------------------

Purpose:
Identify products with the largest peso decreases
in net sales from 2024 to 2025.

Metrics:
- 2024 Net Sales
- 2025 Net Sales
- Sales Difference
- YoY Growth (%)

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_yearly_sales AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,
        year,
        net_sales,

        LAG(net_sales) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_sales

    FROM product_yearly_sales
)

SELECT
    product_name,
    category,

    ROUND(previous_year_sales, 2) AS sales_2024,

    ROUND(net_sales, 2) AS sales_2025,

    ROUND(
        net_sales - previous_year_sales,
        2
    ) AS sales_difference,

    ROUND(
        100.0 * (net_sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS sales_growth_pct

FROM product_comparison

WHERE year = 2025

ORDER BY sales_difference ASC

LIMIT 15;


/*
------------------------------------------------------------
QUERY 4.6: BIGGEST PRODUCT GROSS PROFIT INCREASES
------------------------------------------------------------

Purpose:
Identify products with the largest increases in
gross profit from 2024 to 2025.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_yearly_profit AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,
        year,

        net_sales - net_cogs AS gross_profit,

        net_sales,

        LAG(net_sales - net_cogs) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_profit

    FROM product_yearly_profit
)

SELECT
    product_name,
    category,

    ROUND(previous_year_profit, 2) AS profit_2024,

    ROUND(gross_profit, 2) AS profit_2025,

    ROUND(
        gross_profit - previous_year_profit,
        2
    ) AS profit_difference,

    ROUND(
        100.0 * (gross_profit - previous_year_profit)
        / NULLIF(previous_year_profit, 0),
        2
    ) AS profit_growth_pct

FROM product_comparison

WHERE year = 2025

ORDER BY profit_difference DESC

LIMIT 15;


/*
------------------------------------------------------------
QUERY 4.7: BIGGEST PRODUCT GROSS PROFIT DECLINES
------------------------------------------------------------

Purpose:
Identify products with the largest decreases in
gross profit from 2024 to 2025.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_yearly_profit AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,
        year,

        net_sales - net_cogs AS gross_profit,

        LAG(net_sales - net_cogs) OVER (
            PARTITION BY product_id
            ORDER BY year
        ) AS previous_year_profit

    FROM product_yearly_profit
)

SELECT
    product_name,
    category,

    ROUND(previous_year_profit, 2) AS profit_2024,

    ROUND(gross_profit, 2) AS profit_2025,

    ROUND(
        gross_profit - previous_year_profit,
        2
    ) AS profit_difference,

    ROUND(
        100.0 * (gross_profit - previous_year_profit)
        / NULLIF(previous_year_profit, 0),
        2
    ) AS profit_growth_pct

FROM product_comparison

WHERE year = 2025

ORDER BY profit_difference ASC

LIMIT 15;

/*
============================================================
SECTION 5: PROMOTIONAL EFFECTIVENESS
============================================================

Objectives:
- Compare promoted and non-promoted sales
- Evaluate individual promotion performance
- Compare discount types
- Analyze promotional profitability

*/

/*
------------------------------------------------------------
QUERY 5.1: PROMOTED VS. NON-PROMOTED SALES PERFORMANCE
------------------------------------------------------------

Purpose:
Compare financial performance between promoted and
non-promoted sales.

IMPORTANT NOTE ON ORDER COUNTS:
Promoted and non-promoted order counts are calculated
separately using distinct transaction IDs.

A single transaction may contain both promoted and
non-promoted sales lines. Therefore, the same order
may appear in both groups.

As a result, the two order counts are not mutually
exclusive and should not be added together to calculate
total company orders.
*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

sales_classification AS (
    SELECT
        CASE
            WHEN s.promotion_id IS NULL
                THEN 'Non-Promoted Sales'
            ELSE 'Promoted Sales'
        END AS sales_type,

        s.transaction_id,

        s.gross_sales,
        s.discount_amount,

        s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0) AS net_sales,

        (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost AS net_cogs

    FROM fact_sales s

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id
)

SELECT
    sales_type,

    ROUND(SUM(gross_sales), 2) AS gross_sales,

    ROUND(SUM(discount_amount), 2) AS discounts,

    ROUND(SUM(net_sales), 2) AS net_sales,

    COUNT(DISTINCT transaction_id) AS total_orders,

    ROUND(SUM(net_cogs), 2) AS total_cogs,

    ROUND(
        SUM(net_sales) - SUM(net_cogs),
        2
    ) AS gross_profit,

    ROUND(
        100.0 * (SUM(net_sales) - SUM(net_cogs))
        / NULLIF(SUM(net_sales), 0),
        2
    ) AS gross_profit_margin_pct

FROM sales_classification

GROUP BY sales_type

ORDER BY sales_type;

/*
------------------------------------------------------------
QUERY 5.2: INDIVIDUAL PROMOTION PERFORMANCE
------------------------------------------------------------

Purpose:
Evaluate each promotion based on sales, discounts,
orders, units sold, gross profit, and margin.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

promotion_performance AS (
    SELECT
        p.promotion_id,
        p.promotion_name,
        p.discount_type,
        p.discount_value,

        COUNT(s.sales_line_id) AS sales_lines,

        COUNT(DISTINCT s.transaction_id) AS total_orders,

        SUM(
            s.quantity - COALESCE(r.returned_quantity, 0)
        ) AS net_units_sold,

        SUM(s.gross_sales) AS gross_sales,

        SUM(s.discount_amount) AS discounts,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS total_cogs

    FROM fact_sales s

    JOIN dim_promotions p
        ON s.promotion_id = p.promotion_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        p.promotion_id,
        p.promotion_name,
        p.discount_type,
        p.discount_value
)

SELECT
    promotion_id,
    promotion_name,
    discount_type,
    discount_value,

    sales_lines,
    total_orders,
    net_units_sold,

    ROUND(gross_sales, 2) AS gross_sales,
    ROUND(discounts, 2) AS discounts,
    ROUND(net_sales, 2) AS net_sales,
    ROUND(total_cogs, 2) AS total_cogs,

    ROUND(net_sales - total_cogs, 2) AS gross_profit,

    ROUND(
        100.0 * (net_sales - total_cogs)
        / NULLIF(net_sales, 0),
        2
    ) AS gross_profit_margin_pct

FROM promotion_performance

ORDER BY net_sales DESC;

/*
------------------------------------------------------------
QUERY 5.3: PROMOTION PERFORMANCE BY PRODUCT CATEGORY
------------------------------------------------------------

Purpose:
Compare promoted and non-promoted performance
across product categories.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

category_performance AS (
    SELECT
        p.category,

        CASE
            WHEN s.promotion_id IS NULL
                THEN 'Non-Promoted'
            ELSE 'Promoted'
        END AS sales_type,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS total_cogs

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        p.category,
        sales_type
)

SELECT
    category,

    ROUND(
        MAX(net_sales) FILTER (
            WHERE sales_type = 'Non-Promoted'
        ),
        2
    ) AS non_promoted_sales,

    ROUND(
        100.0 * (
            MAX(net_sales - total_cogs) FILTER (
                WHERE sales_type = 'Non-Promoted'
            )
        ) / NULLIF(
            MAX(net_sales) FILTER (
                WHERE sales_type = 'Non-Promoted'
            ),
            0
        ),
        2
    ) AS non_promoted_margin_pct,

    ROUND(
        MAX(net_sales) FILTER (
            WHERE sales_type = 'Promoted'
        ),
        2
    ) AS promoted_sales,

    ROUND(
        100.0 * (
            MAX(net_sales - total_cogs) FILTER (
                WHERE sales_type = 'Promoted'
            )
        ) / NULLIF(
            MAX(net_sales) FILTER (
                WHERE sales_type = 'Promoted'
            ),
            0
        ),
        2
    ) AS promoted_margin_pct

FROM category_performance

GROUP BY category

ORDER BY category;

/*
------------------------------------------------------------
QUERY 5.4: PERFORMANCE BY DISCOUNT TYPE
------------------------------------------------------------

Purpose:
Compare fixed-amount and percentage-based promotions.

Important:
Only one fixed-amount campaign exists in this dataset.
Results should not be treated as conclusive evidence
that one discount type is inherently better.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

discount_type_performance AS (
    SELECT
        p.discount_type,

        COUNT(s.sales_line_id) AS sales_lines,

        COUNT(DISTINCT s.transaction_id) AS total_orders,

        SUM(
            s.quantity - COALESCE(r.returned_quantity, 0)
        ) AS net_units_sold,

        SUM(s.gross_sales) AS gross_sales,

        SUM(s.discount_amount) AS discounts,

        SUM(
            s.gross_sales
            - s.discount_amount
            - COALESCE(r.refund_amount, 0)
        ) AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS total_cogs

    FROM fact_sales s

    JOIN dim_promotions p
        ON s.promotion_id = p.promotion_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY p.discount_type
)

SELECT
    discount_type,

    sales_lines,
    total_orders,
    net_units_sold,

    ROUND(gross_sales, 2) AS gross_sales,
    ROUND(discounts, 2) AS discounts,
    ROUND(net_sales, 2) AS net_sales,
    ROUND(total_cogs, 2) AS total_cogs,

    ROUND(net_sales - total_cogs, 2) AS gross_profit,

    ROUND(
        100.0 * (net_sales - total_cogs)
        / NULLIF(net_sales, 0),
        2
    ) AS gross_profit_margin_pct

FROM discount_type_performance

ORDER BY discount_type;

/*
============================================================
SECTION 6: INVENTORY ANALYSIS
============================================================

Objectives:
- Analyze stockouts and low-stock conditions
- Identify overstocked branches and products
- Investigate inventory availability in Bacoor
- Compare inventory availability against product demand

*/

/*
------------------------------------------------------------
QUERY 6.1: INVENTORY AVAILABILITY BY BRANCH
------------------------------------------------------------

Purpose:
Evaluate inventory availability across all branches.

Definitions:
- Stockout: quantity_on_hand = 0
- Low Stock: quantity_on_hand > 0 AND quantity_on_hand <= reorder_level

Rates use all inventory snapshots for each branch
as the denominator.

*/

SELECT
    b.branch_name,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand = 0
    ) AS stockout_records,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand > 0
          AND i.quantity_on_hand <= i.reorder_level
    ) AS low_stock_records,

    COUNT(*) AS total_inventory_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand = 0
        ) / COUNT(*),
        2
    ) AS stockout_rate_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand > 0
              AND i.quantity_on_hand <= i.reorder_level
        ) / COUNT(*),
        2
    ) AS low_stock_rate_pct

FROM fact_inventory i

JOIN dim_branches b
    ON i.branch_id = b.branch_id

GROUP BY
    b.branch_id,
    b.branch_name

ORDER BY stockout_rate_pct DESC;

/*
------------------------------------------------------------
QUERY 6.2: PRODUCTS WITH THE MOST STOCKOUT RECORDS
------------------------------------------------------------

Purpose:
Identify products with the highest number of stockout
snapshots across all branches.

*/

SELECT
    p.product_name,
    p.category,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand = 0
    ) AS stockout_records,

    COUNT(*) AS total_inventory_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand = 0
        ) / COUNT(*),
        2
    ) AS stockout_rate_pct

FROM fact_inventory i

JOIN dim_products p
    ON i.product_id = p.product_id

GROUP BY
    p.product_id,
    p.product_name,
    p.category

ORDER BY stockout_records DESC

LIMIT 15;

/*
------------------------------------------------------------
QUERY 6.3: OVERSTOCKED INVENTORY BY BRANCH
------------------------------------------------------------

Purpose:
Identify branches with the highest number and rate
of overstocked inventory snapshots.

Definition:
Overstock = quantity_on_hand >= 3 * reorder_level

*/

SELECT
    b.branch_name,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand >= 3 * i.reorder_level
    ) AS overstock_records,

    COUNT(*) AS total_inventory_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand >= 3 * i.reorder_level
        ) / COUNT(*),
        2
    ) AS overstock_rate_pct

FROM fact_inventory i

JOIN dim_branches b
    ON i.branch_id = b.branch_id

GROUP BY
    b.branch_id,
    b.branch_name

ORDER BY overstock_rate_pct DESC;

/*
------------------------------------------------------------
QUERY 6.4: PERSISTENT OVERSTOCK IN LAS PIÑAS
------------------------------------------------------------

Purpose:
Identify products with the most frequent overstock
conditions in Las Piñas.

Branch ID: BR006
Overstock: quantity_on_hand >= 3 * reorder_level

*/

SELECT
    p.product_name,
    p.category,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand >= 3 * i.reorder_level
    ) AS overstock_records,

    ROUND(
        AVG(i.quantity_on_hand),
        2
    ) AS avg_quantity_on_hand,

    ROUND(
        AVG(i.reorder_level),
        2
    ) AS avg_reorder_level

FROM fact_inventory i

JOIN dim_products p
    ON i.product_id = p.product_id

WHERE i.branch_id = 'BR006'

GROUP BY
    p.product_id,
    p.product_name,
    p.category

HAVING COUNT(*) FILTER (
    WHERE i.quantity_on_hand >= 3 * i.reorder_level
) > 0

ORDER BY
    overstock_records DESC,
    avg_quantity_on_hand DESC

LIMIT 15;

/*
------------------------------------------------------------
QUERY 6.5: STOCKOUT PRODUCTS IN BACOOR
------------------------------------------------------------

Purpose:
Identify products with the most frequent stockouts
in the Bacoor branch.

Branch ID: BR003
Stockout: quantity_on_hand = 0

*/

SELECT
    p.product_name,
    p.category,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand = 0
    ) AS stockout_records,

    COUNT(*) AS total_inventory_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand = 0
        ) / COUNT(*),
        2
    ) AS stockout_rate_pct

FROM fact_inventory i

JOIN dim_products p
    ON i.product_id = p.product_id

WHERE i.branch_id = 'BR003'

GROUP BY
    p.product_id,
    p.product_name,
    p.category

HAVING COUNT(*) FILTER (
    WHERE i.quantity_on_hand = 0
) > 0

ORDER BY stockout_records DESC

LIMIT 15;

/*
------------------------------------------------------------
QUERY 6.6: BACOOR INVENTORY AVAILABILITY BY QUARTER
------------------------------------------------------------

Purpose:
Track stockout and low-stock rates over time
in the Bacoor branch.

Branch ID: BR003

*/

SELECT
    d.year,
    d.quarter,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand = 0
    ) AS stockout_records,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand > 0
          AND i.quantity_on_hand <= i.reorder_level
    ) AS low_stock_records,

    COUNT(*) AS total_inventory_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand = 0
        ) / COUNT(*),
        2
    ) AS stockout_rate_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand > 0
              AND i.quantity_on_hand <= i.reorder_level
        ) / COUNT(*),
        2
    ) AS low_stock_rate_pct

FROM fact_inventory i

JOIN dim_date d
    ON i.date_id = d.date_id

WHERE i.branch_id = 'BR003'

GROUP BY
    d.year,
    d.quarter

ORDER BY
    d.year,
    d.quarter;

/*
------------------------------------------------------------
QUERY 6.7: BACOOR PRODUCT DEMAND VS. INVENTORY AVAILABILITY
------------------------------------------------------------

Purpose:
Compare product sales performance with inventory
availability in Bacoor.

Branch ID: BR003

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_sales AS (
    SELECT
        s.product_id,

        SUM(s.quantity)
            - SUM(COALESCE(r.returned_quantity, 0))
            AS net_units_sold,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales

    FROM fact_sales s

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    WHERE s.branch_id = 'BR003'

    GROUP BY s.product_id
),

product_inventory AS (
    SELECT
        product_id,

        COUNT(*) FILTER (
            WHERE quantity_on_hand = 0
        ) AS stockout_records,

        COUNT(*) AS total_inventory_records,

        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE quantity_on_hand = 0
            ) / COUNT(*),
            2
        ) AS stockout_rate_pct

    FROM fact_inventory

    WHERE branch_id = 'BR003'

    GROUP BY product_id
)

SELECT
    p.product_name,
    p.category,

    COALESCE(ps.net_units_sold, 0) AS net_units_sold,

    ROUND(COALESCE(ps.net_sales, 0), 2) AS net_sales,

    COALESCE(pi.stockout_records, 0) AS stockout_records,

    COALESCE(pi.stockout_rate_pct, 0) AS stockout_rate_pct

FROM dim_products p

LEFT JOIN product_sales ps
    ON p.product_id = ps.product_id

LEFT JOIN product_inventory pi
    ON p.product_id = pi.product_id

ORDER BY
    pi.stockout_records DESC,
    ps.net_units_sold DESC

LIMIT 15;

/*
============================================================
SECTION 7: RETURNS AND REFUNDS ANALYSIS
============================================================

Objectives:
- Analyze returns by category and branch
- Examine monthly return trends
- Compare annual return performance
- Identify products with high return rates

*/

/*
------------------------------------------------------------
QUERY 7.1: RETURNS BY BRANCH AND CATEGORY
------------------------------------------------------------

Purpose:
Analyze return activity across branches and categories.

Metrics:
- Returned units
- Return records
- Total refunds
- Original units sold
- Return rate

*/

WITH sales_summary AS (
    SELECT
        s.branch_id,
        p.category,
        SUM(s.quantity) AS original_units_sold

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    GROUP BY
        s.branch_id,
        p.category
),

returns_summary AS (
    SELECT
        r.branch_id,
        p.category,

        SUM(r.returned_quantity) AS returned_units,
        COUNT(*) AS return_records,
        SUM(r.refund_amount) AS total_refunds

    FROM fact_returns r

    JOIN dim_products p
        ON r.product_id = p.product_id

    GROUP BY
        r.branch_id,
        p.category
)

SELECT
    b.branch_name,
    s.category,

    COALESCE(r.returned_units, 0) AS returned_units,
    COALESCE(r.return_records, 0) AS return_records,

    ROUND(
        COALESCE(r.total_refunds, 0),
        2
    ) AS total_refunds,

    s.original_units_sold,

    ROUND(
        100.0 * COALESCE(r.returned_units, 0)
        / NULLIF(s.original_units_sold, 0),
        2
    ) AS return_rate_pct

FROM sales_summary s

JOIN dim_branches b
    ON s.branch_id = b.branch_id

LEFT JOIN returns_summary r
    ON s.branch_id = r.branch_id
   AND s.category = r.category

ORDER BY
    return_rate_pct DESC,
    returned_units DESC;


/*
------------------------------------------------------------
QUERY 7.2: MONTHLY RETURN TRENDS
------------------------------------------------------------

Purpose:
Analyze monthly return trends based on the original
sale date of returned products.

Return rate:
Returned units / Original units sold * 100

Method:
Returns are attributed to the month of the original sale,
not the date when the return was processed.

*/

WITH monthly_sales AS (
    SELECT
        d.year,
        d.month,
        d.month_name,

        SUM(s.quantity) AS original_units_sold

    FROM fact_sales s

    JOIN dim_date d
        ON s.date_id = d.date_id

    GROUP BY
        d.year,
        d.month,
        d.month_name
),

monthly_returns AS (
    SELECT
        d.year,
        d.month,

        SUM(r.returned_quantity) AS returned_units,
        COUNT(*) AS return_records,
        SUM(r.refund_amount) AS total_refunds

    FROM fact_returns r

    JOIN fact_sales s
        ON r.sales_line_id = s.sales_line_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    GROUP BY
        d.year,
        d.month
)

SELECT
    s.year,
    s.month,
    s.month_name,

    COALESCE(r.returned_units, 0) AS returned_units,
    COALESCE(r.return_records, 0) AS return_records,

    ROUND(
        COALESCE(r.total_refunds, 0),
        2
    ) AS total_refunds,

    s.original_units_sold,

    ROUND(
        100.0 * COALESCE(r.returned_units, 0)
        / NULLIF(s.original_units_sold, 0),
        2
    ) AS return_rate_pct

FROM monthly_sales s

LEFT JOIN monthly_returns r
    ON s.year = r.year
   AND s.month = r.month

ORDER BY
    s.year,
    s.month;


/*
------------------------------------------------------------
QUERY 7.3: ANNUAL RETURN PERFORMANCE
------------------------------------------------------------

Purpose:
Compare annual return activity between 2024 and 2025.

Method:
Returns are attributed to the year of the original sale,
not the year when the return was processed.

*/

WITH annual_sales AS (
    SELECT
        d.year,
        SUM(s.quantity) AS original_units_sold

    FROM fact_sales s

    JOIN dim_date d
        ON s.date_id = d.date_id

    GROUP BY
        d.year
),

annual_returns AS (
    SELECT
        d.year,

        SUM(r.returned_quantity) AS returned_units,
        COUNT(*) AS return_records,
        SUM(r.refund_amount) AS total_refunds

    FROM fact_returns r

    JOIN fact_sales s
        ON r.sales_line_id = s.sales_line_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    GROUP BY
        d.year
)

SELECT
    s.year,

    COALESCE(r.returned_units, 0) AS returned_units,
    COALESCE(r.return_records, 0) AS return_records,

    ROUND(
        COALESCE(r.total_refunds, 0),
        2
    ) AS total_refunds,

    s.original_units_sold,

    ROUND(
        100.0 * COALESCE(r.returned_units, 0)
        / NULLIF(s.original_units_sold, 0),
        2
    ) AS return_rate_pct,

    ROUND(
        COALESCE(r.total_refunds, 0)
        / NULLIF(r.return_records, 0),
        2
    ) AS average_refund_per_record

FROM annual_sales s

LEFT JOIN annual_returns r
    ON s.year = r.year

ORDER BY
    s.year;

/*
------------------------------------------------------------
QUERY 7.4: PRODUCTS WITH HIGH RETURN RATES
------------------------------------------------------------

Purpose:
Identify products with relatively high return rates.

Minimum sales volume:
100 original units

Return rate:
Returned units / Original units sold * 100

*/

WITH product_sales AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,

        SUM(s.quantity) AS original_units_sold

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category
),

product_returns AS (
    SELECT
        product_id,

        SUM(returned_quantity) AS returned_units,
        COUNT(*) AS return_records,
        SUM(refund_amount) AS total_refunds

    FROM fact_returns

    GROUP BY product_id
)

SELECT
    s.product_name,
    s.category,

    COALESCE(r.returned_units, 0) AS returned_units,
    COALESCE(r.return_records, 0) AS return_records,

    ROUND(
        COALESCE(r.total_refunds, 0),
        2
    ) AS total_refunds,

    s.original_units_sold,

    ROUND(
        100.0 * COALESCE(r.returned_units, 0)
        / NULLIF(s.original_units_sold, 0),
        2
    ) AS return_rate_pct

FROM product_sales s

LEFT JOIN product_returns r
    ON s.product_id = r.product_id

WHERE s.original_units_sold >= 100

ORDER BY
    return_rate_pct DESC,
    returned_units DESC

LIMIT 20;

/*
============================================================
SECTION 8: BUSINESS TRENDS AND OPPORTUNITIES
============================================================

Objectives:
- Identify business growth opportunities
- Investigate declining branches and products
- Evaluate sales and profitability trends
- Develop evidence-based recommendations
*/

/*
------------------------------------------------------------
QUERY 8.1: BRANCH PERFORMANCE OPPORTUNITY SCORECARD
------------------------------------------------------------

Purpose:
Compare branch performance between 2024 and 2025.

Metrics:
- Net Sales
- Total Orders
- Average Order Value
- Gross Profit
- Gross Profit Margin

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

branch_year AS (
    SELECT
        s.branch_id,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        COUNT(DISTINCT s.transaction_id) AS total_orders,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.branch_id,
        d.year
),

branch_comparison AS (
    SELECT
        branch_id,

        SUM(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        SUM(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        SUM(total_orders) FILTER (
            WHERE year = 2024
        ) AS orders_2024,

        SUM(total_orders) FILTER (
            WHERE year = 2025
        ) AS orders_2025,

        SUM(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        SUM(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM branch_year
    GROUP BY branch_id
)

SELECT
    b.branch_name,

    ROUND(s.sales_2024, 2) AS sales_2024,
    ROUND(s.sales_2025, 2) AS sales_2025,

    ROUND(
        100.0 * (s.sales_2025 - s.sales_2024)
        / NULLIF(s.sales_2024, 0),
        2
    ) AS sales_growth_pct,

    s.orders_2024,
    s.orders_2025,

    ROUND(
        100.0 * (s.orders_2025 - s.orders_2024)
        / NULLIF(s.orders_2024, 0),
        2
    ) AS order_growth_pct,

    ROUND(
        s.sales_2024 / NULLIF(s.orders_2024, 0),
        2
    ) AS aov_2024,

    ROUND(
        s.sales_2025 / NULLIF(s.orders_2025, 0),
        2
    ) AS aov_2025,

    ROUND(
        100.0 * (
            (s.sales_2025 / NULLIF(s.orders_2025, 0))
            - (s.sales_2024 / NULLIF(s.orders_2024, 0))
        )
        / NULLIF(
            s.sales_2024 / NULLIF(s.orders_2024, 0),
            0
        ),
        2
    ) AS aov_growth_pct,

    ROUND(s.profit_2024, 2) AS profit_2024,
    ROUND(s.profit_2025, 2) AS profit_2025,

    ROUND(
        100.0 * (s.profit_2025 - s.profit_2024)
        / NULLIF(s.profit_2024, 0),
        2
    ) AS profit_growth_pct,

    ROUND(
        100.0 * s.profit_2024
        / NULLIF(s.sales_2024, 0),
        2
    ) AS margin_2024_pct,

    ROUND(
        100.0 * s.profit_2025
        / NULLIF(s.sales_2025, 0),
        2
    ) AS margin_2025_pct

FROM branch_comparison s

JOIN dim_branches b
    ON s.branch_id = b.branch_id

ORDER BY sales_growth_pct DESC;

/*
------------------------------------------------------------
QUERY 8.2: CATEGORY GROWTH AND PROFITABILITY OPPORTUNITIES
------------------------------------------------------------

Purpose:
Identify product categories with strong or weak
sales and gross profit performance.

Comparison: 2024 vs. 2025

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

category_year AS (
    SELECT
        p.category,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        p.category,
        d.year
),

category_comparison AS (
    SELECT
        category,

        SUM(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        SUM(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        SUM(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        SUM(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM category_year
    GROUP BY category
)

SELECT
    category,

    ROUND(sales_2024, 2) AS sales_2024,
    ROUND(sales_2025, 2) AS sales_2025,

    ROUND(
        100.0 * (sales_2025 - sales_2024)
        / NULLIF(sales_2024, 0),
        2
    ) AS sales_growth_pct,

    ROUND(profit_2024, 2) AS profit_2024,
    ROUND(profit_2025, 2) AS profit_2025,

    ROUND(
        100.0 * (profit_2025 - profit_2024)
        / NULLIF(profit_2024, 0),
        2
    ) AS profit_growth_pct,

    ROUND(
        100.0 * profit_2025
        / NULLIF(sales_2025, 0),
        2
    ) AS margin_2025_pct

FROM category_comparison

ORDER BY profit_growth_pct DESC;

/*
------------------------------------------------------------
QUERY 8.3: HIGH-REVENUE PRODUCTS WITH DECLINING PROFIT
------------------------------------------------------------

Purpose:
Identify significant products whose gross profit
declined despite generating meaningful revenue.

Criteria:
- 2025 net sales >= PHP 100,000
- 2025 gross profit < 2024 gross profit

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_year AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,

        MAX(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        MAX(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        MAX(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        MAX(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM product_year

    GROUP BY
        product_id,
        product_name,
        category
)

SELECT
    product_name,
    category,

    ROUND(sales_2025, 2) AS sales_2025,

    ROUND(
        sales_2025 - sales_2024,
        2
    ) AS sales_difference,

    ROUND(
        profit_2024,
        2
    ) AS profit_2024,

    ROUND(
        profit_2025,
        2
    ) AS profit_2025,

    ROUND(
        profit_2025 - profit_2024,
        2
    ) AS profit_difference,

    ROUND(
        100.0 * profit_2025
        / NULLIF(sales_2025, 0),
        2
    ) AS margin_2025_pct

FROM product_comparison

WHERE sales_2025 >= 100000
  AND profit_2025 < profit_2024

ORDER BY profit_difference ASC;

/*
------------------------------------------------------------
QUERY 8.4: HIGH-REVENUE PRODUCTS WITH LOW PROFIT MARGINS
------------------------------------------------------------

Purpose:
Identify products generating meaningful revenue
but retaining less than 20% as gross profit.

Criteria:
- 2025 net sales >= PHP 100,000
- 2025 gross profit margin < 20%

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_2025 AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    WHERE d.year = 2025

    GROUP BY
        s.product_id,
        p.product_name,
        p.category
)

SELECT
    product_name,
    category,

    ROUND(net_sales, 2) AS net_sales,
    ROUND(net_cogs, 2) AS net_cogs,
    ROUND(gross_profit, 2) AS gross_profit,

    ROUND(
        100.0 * gross_profit
        / NULLIF(net_sales, 0),
        2
    ) AS gross_profit_margin_pct

FROM product_2025

WHERE net_sales >= 100000
  AND 100.0 * gross_profit / NULLIF(net_sales, 0) < 20

ORDER BY gross_profit DESC;

/*
------------------------------------------------------------
QUERY 8.5: PRODUCT-LEVEL BUSINESS WARNING SIGNS
------------------------------------------------------------

Purpose:
Identify products with multiple sales, profitability,
and inventory warning signs.

Conditions:
1. Declining net sales
2. Declining gross profit
3. Gross profit margin below 20%
4. Persistent Las Piñas overstock (>= 80 snapshots)
5. Frequent Bacoor stockouts (>= 30 snapshots)

A product is flagged if at least two conditions apply.

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_year AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,

        MAX(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        MAX(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        MAX(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        MAX(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM product_year

    GROUP BY
        product_id,
        product_name,
        category
),

inventory_flags AS (
    SELECT
        product_id,

        COUNT(*) FILTER (
            WHERE branch_id = 'BR006'
              AND quantity_on_hand >= 3 * reorder_level
        ) AS las_pinas_overstock_records,

        COUNT(*) FILTER (
            WHERE branch_id = 'BR003'
              AND quantity_on_hand = 0
        ) AS bacoor_stockout_records

    FROM fact_inventory

    GROUP BY product_id
),

risk_assessment AS (
    SELECT
        pc.*,

        ROUND(
            100.0 * pc.profit_2025
            / NULLIF(pc.sales_2025, 0),
            2
        ) AS margin_2025_pct,

        COALESCE(i.las_pinas_overstock_records, 0)
            AS las_pinas_overstock_records,

        COALESCE(i.bacoor_stockout_records, 0)
            AS bacoor_stockout_records,

        CASE
            WHEN pc.sales_2025 < pc.sales_2024
            THEN 1 ELSE 0
        END AS declining_sales_flag,

        CASE
            WHEN pc.profit_2025 < pc.profit_2024
            THEN 1 ELSE 0
        END AS declining_profit_flag,

        CASE
            WHEN 100.0 * pc.profit_2025
                 / NULLIF(pc.sales_2025, 0) < 20
            THEN 1 ELSE 0
        END AS low_margin_flag,

        CASE
            WHEN COALESCE(i.las_pinas_overstock_records, 0) >= 80
            THEN 1 ELSE 0
        END AS persistent_overstock_flag,

        CASE
            WHEN COALESCE(i.bacoor_stockout_records, 0) >= 30
            THEN 1 ELSE 0
        END AS frequent_stockout_flag

    FROM product_comparison pc

    LEFT JOIN inventory_flags i
        ON pc.product_id = i.product_id
)

SELECT
    product_name,
    category,

    ROUND(sales_2025, 2) AS sales_2025,

    ROUND(
        profit_2025 - profit_2024,
        2
    ) AS profit_difference,

    margin_2025_pct,

    las_pinas_overstock_records,
    bacoor_stockout_records,

    declining_sales_flag
    + declining_profit_flag
    + low_margin_flag
    + persistent_overstock_flag
    + frequent_stockout_flag
        AS warning_sign_count

FROM risk_assessment

WHERE
    declining_sales_flag
    + declining_profit_flag
    + low_margin_flag
    + persistent_overstock_flag
    + frequent_stockout_flag >= 2

ORDER BY
    warning_sign_count DESC,
    sales_2025 DESC;

/*
------------------------------------------------------------
QUERY 8.6: PRODUCTS WITH POSITIVE SALES AND PROFIT GROWTH
------------------------------------------------------------

Purpose:
Identify products demonstrating both revenue growth
and gross profit improvement.

Comparison: 2024 vs. 2025

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_year AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,

        MAX(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        MAX(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        MAX(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        MAX(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM product_year

    GROUP BY
        product_id,
        product_name,
        category
)

SELECT
    product_name,
    category,

    ROUND(sales_2024, 2) AS sales_2024,
    ROUND(sales_2025, 2) AS sales_2025,

    ROUND(
        100.0 * (sales_2025 - sales_2024)
        / NULLIF(sales_2024, 0),
        2
    ) AS sales_growth_pct,

    ROUND(
        profit_2025 - profit_2024,
        2
    ) AS profit_increase,

    ROUND(
        100.0 * (profit_2025 - profit_2024)
        / NULLIF(profit_2024, 0),
        2
    ) AS profit_growth_pct,

    ROUND(
        100.0 * profit_2025
        / NULLIF(sales_2025, 0),
        2
    ) AS margin_2025_pct

FROM product_comparison

WHERE sales_2025 > sales_2024
  AND profit_2025 > profit_2024

ORDER BY profit_increase DESC

LIMIT 15;

/*
------------------------------------------------------------
QUERY 8.7: GROWING PRODUCTS VS. INVENTORY AVAILABILITY
------------------------------------------------------------

Purpose:
Compare product sales/profit growth against inventory
conditions across all branches.

Inventory indicators:
- Stockout: quantity_on_hand = 0
- Low stock: quantity_on_hand > 0 and
             quantity_on_hand <= reorder_level
- Overstock: quantity_on_hand >= 3 * reorder_level

*/

WITH returns_by_line AS (
    SELECT
        sales_line_id,
        SUM(returned_quantity) AS returned_quantity,
        SUM(refund_amount) AS refund_amount
    FROM fact_returns
    GROUP BY sales_line_id
),

product_year AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category,
        d.year,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            AS net_sales,

        SUM(
            (s.quantity - COALESCE(r.returned_quantity, 0))
            * s.unit_cost
        ) AS net_cogs,

        SUM(s.gross_sales)
            - SUM(s.discount_amount)
            - SUM(COALESCE(r.refund_amount, 0))
            - SUM(
                (s.quantity - COALESCE(r.returned_quantity, 0))
                * s.unit_cost
            ) AS gross_profit

    FROM fact_sales s

    JOIN dim_products p
        ON s.product_id = p.product_id

    JOIN dim_date d
        ON s.date_id = d.date_id

    LEFT JOIN returns_by_line r
        ON s.sales_line_id = r.sales_line_id

    GROUP BY
        s.product_id,
        p.product_name,
        p.category,
        d.year
),

product_comparison AS (
    SELECT
        product_id,
        product_name,
        category,

        MAX(net_sales) FILTER (
            WHERE year = 2024
        ) AS sales_2024,

        MAX(net_sales) FILTER (
            WHERE year = 2025
        ) AS sales_2025,

        MAX(gross_profit) FILTER (
            WHERE year = 2024
        ) AS profit_2024,

        MAX(gross_profit) FILTER (
            WHERE year = 2025
        ) AS profit_2025

    FROM product_year

    GROUP BY
        product_id,
        product_name,
        category
),

inventory_summary AS (
    SELECT
        product_id,

        COUNT(*) FILTER (
            WHERE quantity_on_hand = 0
        ) AS stockout_records,

        COUNT(*) FILTER (
            WHERE quantity_on_hand > 0
              AND quantity_on_hand <= reorder_level
        ) AS low_stock_records,

        COUNT(*) FILTER (
            WHERE quantity_on_hand >= 3 * reorder_level
        ) AS overstock_records,

        ROUND(
            AVG(quantity_on_hand),
            2
        ) AS average_stock

    FROM fact_inventory

    GROUP BY product_id
)

SELECT
    pc.product_name,
    pc.category,

    ROUND(
        pc.sales_2025 - pc.sales_2024,
        2
    ) AS sales_increase,

    ROUND(
        pc.profit_2025 - pc.profit_2024,
        2
    ) AS profit_increase,

    ROUND(
        100.0 * pc.profit_2025
        / NULLIF(pc.sales_2025, 0),
        2
    ) AS margin_2025_pct,

    i.stockout_records,
    i.low_stock_records,
    i.overstock_records,
    i.average_stock

FROM product_comparison pc

JOIN inventory_summary i
    ON pc.product_id = i.product_id

WHERE pc.sales_2025 > pc.sales_2024
  AND pc.profit_2025 > pc.profit_2024

ORDER BY
    i.stockout_records DESC,
    i.low_stock_records DESC,
    profit_increase DESC

LIMIT 20;

/*
------------------------------------------------------------
QUERY 8.8: BRANCH-LEVEL INVENTORY CONDITIONS
------------------------------------------------------------

Purpose:
Compare inventory conditions across branches for
selected products identified in QUERY 8.7.

Product selection methodology:
The shortlist contains eight products from QUERY 8.7:
- Four products with recorded stockout snapshots.
- Four products with persistent low-stock conditions.

The selection is based on the inventory findings
from the preceding analysis. This is a focused
investigation, not a complete inventory assessment
of all 120 products.

Note:
The product list is intentionally fixed based on
the results of QUERY 8.7. If the shortlist changes,
update the product filters below accordingly.
*/

SELECT
    p.product_name,
    b.branch_name,

    COUNT(*) AS inventory_snapshots,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand = 0
    ) AS stockout_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand = 0
        ) / COUNT(*),
        2
    ) AS stockout_rate_pct,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand > 0
          AND i.quantity_on_hand <= i.reorder_level
    ) AS low_stock_records,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE i.quantity_on_hand > 0
              AND i.quantity_on_hand <= i.reorder_level
        ) / COUNT(*),
        2
    ) AS low_stock_rate_pct,

    COUNT(*) FILTER (
        WHERE i.quantity_on_hand >= 3 * i.reorder_level
    ) AS overstock_records,

    ROUND(
        AVG(i.quantity_on_hand),
        2
    ) AS average_stock

FROM fact_inventory i

JOIN dim_products p
    ON i.product_id = p.product_id

JOIN dim_branches b
    ON i.branch_id = b.branch_id

WHERE p.product_name IN (
    'Laundry Bar Soap',
    'Cooking Oil 1L',
    'Greek Yogurt 400g',
    'Deodorant Roll-On',
    'Aluminum Foil 10m',
    'Cola 1.5L',
    'Insect Spray 500ml',
    'Iced Tea 500ml'
)

GROUP BY
    p.product_id,
    p.product_name,
    b.branch_id,
    b.branch_name

ORDER BY
    p.product_name,
    stockout_rate_pct DESC,
    low_stock_rate_pct DESC;

/*
============================================================
END OF BUSINESS ANALYSIS
============================================================
*/