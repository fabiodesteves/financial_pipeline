with source as (
    select * from {{ source('raw', 'raw_financials') }}
),

renamed as (
    select
        -- identifier
        "Ticker"                    as ticker,

        -- income statement
        "Revenue"                   as revenue,
        "Net income"                as net_income,
        "Operating income"          as operating_income,

        -- balance sheet
        "Total debt"                as total_debt,
        "Equity"                    as equity,
        "Liabilities"               as liabilities,
        "Cash and equivalents"      as cash_and_equivalents,

        -- market data
        "Market cap"                as market_cap,

        -- cash flow
        "Free cash flow"            as free_cash_flow,
        "Buyback"                   as buyback,

        -- yields
        "Dividend (Raw)"          as dividend_yield

    from source
)

select * from renamed