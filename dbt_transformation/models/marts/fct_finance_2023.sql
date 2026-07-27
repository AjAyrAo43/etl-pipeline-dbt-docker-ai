with finance as  (
    select * from {{ ref ('stg_finance_2023') }}
),

final as (
    select
        year,
        case
            when units = 'Dollars (millions)' 
              then cast(
                       nullif(regexp_replace(value, '[^0-9\.\-]', '', 'g'), '') 
                       as numeric
                   ) * 1000000
            else cast(
                       nullif(regexp_replace(value, '[^0-9\.\-]', '', 'g'), '') 
                       as numeric
                   )
        end as value,
        case
            when lower(units) like 'dollars%' then 'Dollars'
            else units
        end as units,
        variable_code
    from finance
)

select * from final