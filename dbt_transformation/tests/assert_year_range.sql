-- Custom dbt test: Asserts that calendar reporting years fall within reasonable enterprise bounds (2000 - 2030)
select
    year,
    variable_code
from {{ ref('fct_finance_2023') }}
where year < 2000 or year > 2030
