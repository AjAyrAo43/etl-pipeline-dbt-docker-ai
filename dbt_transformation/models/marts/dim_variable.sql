with stg_data as (
    select * from {{ ref('stg_finance_2023') }}
),

distinct_variables as (
    select distinct
        variable_code,
        units
    from stg_data
    where variable_code is not null
)

select
    row_number() over (order by variable_code) as variable_key,
    variable_code,
    units
from distinct_variables
