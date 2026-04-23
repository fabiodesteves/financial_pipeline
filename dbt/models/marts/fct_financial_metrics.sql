with base as (
    select * from {{ ref('stg_financials') }}
),

millions as (
    select
        ticker,
        round(market_cap / 1000000, 3)          as market_cap_m,
        round(net_income / 1000000, 3)          as net_income_m,
        round(revenue / 1000000, 3)             as revenue_m,
        round(operating_income / 1000000, 3)    as operating_income_m,
        round(total_debt / 1000000, 3)          as total_debt_m,
        round(cash_and_equivalents/1000000, 3)  as cash_and_equivalents_m,
        round(free_cash_flow/1000000, 3)        as free_cash_flow_m,
        round(dividend_yield * 100, 2)          as dividend_yield_pct
        round(buyback/1000000, 3)               as buyback_m
    from base
),

with_ev as (
    select
        *,
        market_cap_m + total_debt_m - cash_and_equivalents_m   as enterprise_value_m
    from millions
),

with_ratios as (
    select
        *,
        enterprise_value_m / NULLIF(operating_income_m, 0)   as ev_to_ebit
    from with_ev
)

select * from with_ratios