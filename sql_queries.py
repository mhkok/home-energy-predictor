import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

power_usage_home_drop           = "DROP TABLE IF EXISTS power_usage_home"
time_table_drop                 = "DROP TABLE IF EXISTS time"
weather_table_drop              = "DROP TABLE IF EXISTS weather"
electricity_prices_drop         = "DROP TABLE IF EXISTS electricity_prices"
staging_power_usage_drop        = "DROP TABLE IF EXISTS staging_power_usage"

# CREATE TABLES
staging_power_usage_copy = (
    """
    COPY staging_power_usage from 's3://p1-staging/'
    CREDENTIALS 'aws_iam_role={}'
    REGION 'eu-west-1'
    JSON 'auto';
    """
    ).format(config.get('IAM_ROLE', 'ARN'))

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

power_usage_home_create = (
    """
    CREATE TABLE IF NOT EXISTS power_usage_home (
        id INT IDENTITY(0,1),
        datetime timestamp NOT NULL,
        current_power_usage float,
        peak_hours float,
        peak_hours_returned float,
        off_peak_hours float,
        off_peak_returned float,
        current_power_returned,
        CONSTRAINT power_usage_date_id_pkey PRIMARY KEY (power_usage_date_id)
        FOREIGN KEY (datetime) REFERENCES datetime (time),
        FOREIGN KEY (datetime) REFERENCES weather_date_id (weather),
        FOREIGN KEY (datetime) REFERENCES elec_prices_date_id (electricity_prices),
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
        elec_prices_date_id timestamp NOT NULL,
        costperkwh float,
        month varchar(256),
        year int4,
        CONSTRAINT elec_prices_date_id_pkey PRIMARY KEY (elec_prices_date_id)
    );
    """
)

# songplay_table_insert = (
#     """
#    INSERT INTO songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
#    SELECT DISTINCT  se.ts,
#                     se.userid,
#                     se.level,
#                     ss.song_id,
#                     ss.artist_id,
#                     se.sessionid,
#                     se.location,
#                     se.useragent
#     FROM staging_events se 
#     LEFT JOIN staging_songs ss ON (se.artist = ss.artist_name) 
#     AND (se.length = ss.duration)
#     WHERE se.page = 'NextSong' AND artist_id IS NOT NULL;
#     """
# )

# QUERY LISTS

#create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create]
#drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
#copy_table_queries = [staging_events_copy, staging_songs_copy]
#insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
