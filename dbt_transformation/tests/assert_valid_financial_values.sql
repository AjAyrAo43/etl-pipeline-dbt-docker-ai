-- Singular dbt test: Fails if any financial record has invalid negative year or missing values
select
    year,
    value,
    variable_code
from {{ ref('fct_finance_2023') }}
where year < 2000 
   or variable_code is null
