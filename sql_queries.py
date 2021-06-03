import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

power_usage_home_drop           = "DROP TABLE IF EXISTS power_usage_home CASCADE"
time_table_drop                 = "DROP TABLE IF EXISTS time"
weather_table_drop              = "DROP TABLE IF EXISTS weather"
electricity_prices_drop         = "DROP TABLE IF EXISTS electricity_prices CASCADE"
home_electricity_costs_drop     = "DROP TABLE IF EXISTS home_electricity_costs"
staging_power_usage_drop        = "DROP TABLE IF EXISTS staging_power_usage"
staging_electricity_prices_drop = "DROP TABLE IF EXISTS staging_electricity_prices"



## COPY
staging_power_usage_copy = (
    """
    COPY staging_power_usage from 's3://p1-staging/'
    CREDENTIALS 'aws_iam_role={}'
    REGION 'eu-west-1'
    JSON 'auto';
    """
    ).format(config.get('IAM_ROLE', 'ARN'))

# CREATE TABLES

staging_power_usage_create = (
    """
    CREATE TABLE IF NOT EXISTS staging_power_usage (
        datetime varchar,
        current_power_usage_kwh float,
        gas_usage_m3 float,
        peak_hours_kwh float,
        peak_hours_returned_kwh float,
        off_peak_hours_kwh float,
        off_peak_hours_returned_kwh float,
        current_power_returned_kwh float
    )
    """
)

staging_electricity_prices = (
    """
    CREATE TABLE staging_electricity_prices (
        index int, 
        elec_prices_date_id date NOT NULL,
        costperkwh varchar,
        month varchar(256),
        year int4
    );
    """
)

## DIMENSION TABLES
power_usage_home_create = (
    """
    CREATE TABLE IF NOT EXISTS power_usage_home (
        power_usage_date_id bigint NOT NULL,
        datetime timestamp,
        month int,
        year int,
        current_power_usage float,
        peak_hours float,
        peak_hours_returned float,
        off_peak_hours float,
        off_peak_hours_returned float,
        current_power_returned float,
        CONSTRAINT power_usage_date_id_pkey PRIMARY KEY (power_usage_date_id)
    );
    """
)

time_table_create = (
    """
    CREATE TABLE IF NOT EXISTS "time" (
        datetime timestamp NOT NULL,
        "hour" int4,
        "day" int4,
        week int4,
        "month" varchar(256),
        "year" int4,
        weekday varchar(256),
        CONSTRAINT date_pkey PRIMARY KEY (datetime)
    );
    """
)

weather_table_create = (
    """
    CREATE TABLE weather (
        weather_date_id timestamp NOT NULL,
        temperature float,
        month varchar(256),
        year int4,
        CONSTRAINT weather_date_id_pkey PRIMARY KEY (weather_date_id)
    );
    """
)

electricity_prices_create = (
    """
    CREATE TABLE electricity_prices (
        elec_prices_date_id int NOT NULL,
        costperkwh float,
        month varchar(256),
        year int4,
        CONSTRAINT elec_prices_date_id_pkey PRIMARY KEY (elec_prices_date_id)
    );
    """
)

## FACT TABLE
home_electricity_costs = (
    """
    CREATE TABLE IF NOT EXISTS home_electricity_costs (
        id INT IDENTITY(0,1),
        month VARCHAR,
        year INT4,
        electricity_costs_per_month FLOAT,
        power_usage_date_id bigint,
        elec_prices_date_id bigint,
        FOREIGN KEY (power_usage_date_id) REFERENCES power_usage_home (power_usage_date_id),
        FOREIGN KEY (elec_prices_date_id) REFERENCES electricity_prices (elec_prices_date_id)
    )
    """
)

### INSERT SQL STATEMENTS 
power_usage_home_insert = (
    """
    INSERT INTO power_usage_home (power_usage_date_id, datetime, month, year, current_power_usage, peak_hours, peak_hours_returned, off_peak_hours, off_peak_hours_returned, current_power_returned)
                SELECT DISTINCT CAST (regexp_replace(spu.datetime, '[-]')AS BIGINT) AS power_usage_date_id,
                    to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI') AS datetime, 
                    EXTRACT (MONTH FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as month,
                    EXTRACT (YEAR FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as year,                          
                    spu.current_power_usage_kwh,
                    spu.peak_hours_kwh,
                    spu.peak_hours_returned_kwh,
                    spu.off_peak_hours_kwh,
                    spu.off_peak_hours_returned_kwh,
                    spu.current_power_returned_kwh
    FROM staging_power_usage spu
    WHERE spu.datetime IS NOT NULL
    """
)

time_insert = (
    """
    INSERT  INTO time (datetime, hour, day, week, month, year, weekday)
    SELECT  DISTINCT to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI') AS datetime,
            EXTRACT (HOUR FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as hour,
            EXTRACT (DAY FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as day,
            EXTRACT (WEEK FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as week,
            EXTRACT (MONTH FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as month,
            EXTRACT (YEAR FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as year,   
            EXTRACT (WEEKDAY FROM (to_timestamp(spu.datetime, 'DD-MM-YYYY-HH24-MI'))) as weekday
    FROM staging_power_usage spu
    WHERE spu.datetime IS NOT NULL
    """
)

electricity_prices_insert = (
    """
    INSERT INTO electricity_prices (elec_prices_date_id, costperkwh, month, year)
    SELECT DISTINCT CAST (regexp_replace(sep.elec_prices_date_id, '[-]')AS BIGINT) AS elec_prices_date_id,
                    CAST (sep.costperkwh AS float) AS costperkwh,
                    EXTRACT (MONTH FROM sep.elec_prices_date_id) AS month,
                    EXTRACT (YEAR FROM sep.elec_prices_date_id) AS year
    FROM staging_electricity_prices sep
    """
)

home_electricity_costs_table_insert = (
    """
    INSERT INTO home_electricity_costs (month, year, electricity_costs_per_month)
    SELECT DISTINCT puh.month AS month,
    	   			puh.year AS year,
           			SUM(puh.current_power_usage) * ep.costperkwh AS electricity_costs_per_month 
    FROM power_usage_home puh
    JOIN electricity_prices ep ON (puh.month = ep.month)
    AND (ep.year = puh.year)
	GROUP BY puh.month, puh.year, ep.costperkwh
    """
)

# QUERY LISTS

create_table_queries = [staging_power_usage_create, staging_electricity_prices, power_usage_home_create, weather_table_create, electricity_prices_create, time_table_create, home_electricity_costs]
drop_table_queries = [power_usage_home_drop, time_table_drop, weather_table_drop, electricity_prices_drop, home_electricity_costs_drop, staging_power_usage_drop, staging_electricity_prices_drop, time_table_drop]
copy_table_queries = [staging_power_usage_copy]
insert_table_queries = [electricity_prices_insert, power_usage_home_insert, time_insert, home_electricity_costs_table_insert]
