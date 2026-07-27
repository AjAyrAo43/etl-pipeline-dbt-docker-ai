with stg_data as (
    select * from {{ ref('stg_finance_2023') }}
),

distinct_years as (
    select distinct
        year
    from stg_data
    where year is not null
)

select
    year as year_key,
    year as calendar_year
from distinct_years
