-- Custom dbt test: Asserts that financial values are non-negative numeric quantities
select
    year,
    value,
    variable_code
from {{ ref('fct_finance_2023') }}
where value < 0
