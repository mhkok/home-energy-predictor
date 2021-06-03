# home-energy-predictor

## Introduction
This project retrieves data from your smart meter and pushes into dwh for analysis, combined with several external data sources like weather (future relase), weather forecasts (future release) and electricity prices. Currently this code will allow you to calculate costs on your current power usage in your house based on the latest electricity prices.


## Architecture
The architecture of the Home Energy Predictor consists of a myriad of technologies. Streaming data is being collected from your Raspberry Pi through a P1 cable into the cloud (S3 blob storage). On a daily basis an Airflow data pipeline is run to push the data into AWS Redshift (future release). 

![Architecture Home Energy Predictor](./architecture.png)

## Choice of Technology
For data storage I have chosen to use S3 since this is extremely scalable, cheap and quite easy to integrate with a myriad of cloud native technologies out there. 

As for database technology I have chose to use AWS Redshift since this is heavily based on SQL technology, which is again highly scalable and is commonly used by many. This allows for easy transfer of knowledge and is easy understandable by other colleagues in the data engineering world.

As for languages  I have used a combination of SQL, Python and Pandas to be able to extract, transfer and load the data into the Redshift DWH. These are all languages and tools heavily used by the community and are easy understandable. Hence, my decision to use these tools. 

## Different Scenarios
- Data increased by 100x: Due to the scalability of the architecture shown above this should not be an issue for the Energy Predictor tool. If performance does decrease a few options are available in Redshift to improve query performance:
  * Distribution Style tweaks: EVEN for fact tables/dimension tables, ALL, AUTO
  * Sorting Key: define its columns as sort key. Upon loading rows are sorted before distibution slices. This minimizes the query time since each node already has contiguous ranges of rows based on the sorting key. This is useful for columns that are used frequently in sorting like the data dimension and its corresponding FOREIGN key in the fact table.
- Pipelines each day at 7am: By implementing a DAG using Airflow its quite easy to run the ETL processes daily on 7am. 
- Database accessed by 100+ users: The DWH Redshift database can handle up to 500 concurrent connections. Also, most likely when there are more users connected to the Redshift database the hardware specs of the Redshift database will need to be increased to handle the load. If users don't need to perform INSERT or UPDATE it would also be possible to periodically copy the data to a NoSQL database like Cassandra. 

## Data, Data types & Files
This section describes the total amount of data, data types and files in the repository. 

### Data
In the `/data` dir in this repo you can find examples of the original data that's been used in this project. Please note that in the `S3:/p1-staging` bucket around ~1 million JSON files are stored related to power usage, coming from the P1 smartmeter connection. This data is partially artificial and partially live data, to adhere to the project requiremnts. 

### Data types

Currently two different data types are used in this projecct to process data: JSON & CSV. Find under the `/data` dir examples of these files. 
- Electricity Costs data (CSV): This data is coming from the Dutch statistics bureau. This data is used to calculate how much the usage of electricity will cost based on kWh per month
- Power usage (JSON): This data is coming directly from your (compatible) smart meter in your home using a P1 cable connected to a Raspberry Pi. This JSON is an example of how this looks like. Typically the following the data is tracked in the JSON:
```{"current_power_usage_kwh": 0.033, "gas_usage_m3": 631.549, "datetime": "31-05-2021-23-55", "peak_hours_kwh": 3083.134, "peak_hours_returned_kwh": 223.795, "off_peak_hours_kwh": 2491.676, "off_peak_hours_returned_kwh": 102.211, "current_power_returned_kwh": 0.0}```

The following files are in this repo:
- `create_tables.py`: this python file creates the tables that are required to load and ingest the data into the redshift database
- `etl.py`: This file processes the different data sources into the proper dimension & fact tables
- `p1_data_p1.py`: This file is run every 5 mins on a Raspberry Pi connected to the Smartmeter. The python file reads the output of the data and translates this into a JSON file. Finally, the JSON is copied across into S3.
- `terraform/*`: this directory contains all the IaC to provision Airflow & AWS Redshift. Make sure to have installed `terraform 0.13` to properly run this code. To provision infrastructure run the following commands: `terraform init`, `terraform plan` and `terraform apply`.

## Schema, Data Dictionary and Datamodel for DWH

In this section the schema's for the database are explained. The data schema is based on a Star schema, using a physical model. Generally speaking a Star schema has several dimension tables and a fact table. The star schema consists of one or more fact tables referencing any number of dimension tables. The benefits are that the tables are denormalized, queries are simplified and aggregations will go faster. Drawbacks of the star schema model is decreased query flexbility and many to many relationships. This could negatively impact the performance of the database. 

### Star Schema vs Snowflake Schema
I have chose the star schema built on top of Redshift DWH to ensure maintainability and scalability. The type of data used fits nicely for this purpose. The data can be sliced into dimesion tables (eg power usage, electricity prices) and one fact table to view the costs of electricity. 
A snowflake schema is used when you have multiple levels of relationships and child tables have multiple parents. This is not the case for the type of data used in this project, hence the reason I have used a star schema.

### Data Dictionary
`Fact_Home_Electricity_Costs`: This is the fact table that shows the costs per month for your live electricity usage. This table has the following schema:
- `elec_prices_date_id`, `electricity_costs_per_month	`, `month`, `year`

| Field Name | Datatype | Field Length / Precision | Constraint | Description |
| --------------- | --------------- | --------------- | -------- | --------- |
| elec_prices_date_id | INT IDENTITY | 10 / 10 | NOT NULL | This is the field that uniquely identifies the value of the row |
| month | VARCHAR | 256 / 256 | N/A | This column shows the the month |
| electricity_costs_per_month | FLOAT8 | 17 / 17 | N/A | This is the calculation of the cost per month of electricity based on table `power_usage_home` & `Electricity prices`. |
| power_usage_date_id | INT8 | 19 / 19 | FOREIGN KEY | FOREIGN KEY to `power_usage_home` table with primary key `power_usage_date_id` |
| elec_prices_date_id | INT8 | 19 / 19 | FOREIGN KEY | FOREIGN KEY to `electricity_prices` table with primary key `elec_prices_date_id` |
| date | TIMESTAMP | 29 /29 | FOREIGN KEY | FOREIGN KEY to `time` table with primary key `datetime` |


`Dim_Power_Usage`: This is a dimension table consisting of all electricity usage coming from your P1/Smartmeter data deployed on 
Raspbery Pi. This table has the following schema:
- `power_usage_date_id`, `current_power_usage`, `peak_hours`, `peak_hours_returned`, `off_peak_hours`, `off_peak_hours_returned`, `current_power_returned`

| Field Name | Datatype | Field Length / Precision | Constraint | Description |
| --------------- | --------------- | --------------- | -------- | --------- |
| power_usage_date_id | INT8 | 19 / 19 | NOT NULL PRIMARY KEY | This is the unique ID for each of the rows in the table |
| datetime | TIMESTAMP | 29 / 29 | N/A | This is the timestamp of the measure power usage in the house | 
| month | INT4 | 10 / 10 | N/A | This is the month of the power measurement in the house | 
| year |  INT4 | 10 / 10 | N/A | This is the year of the power measurement in the house | 
| current_power_usage | FLOAT8 | 17 / 17 | N/A | This is the current power usage in the house in kwh |
| peak_hours | FLOAT8 | 17 / 17 | N/A | This is the current power usage during peak hours in kwh |
| peak_hours_returned | FLOAT8 | 17 / 17 | N/A | This is current returned power to the elecricity supplier in kwh | 
| off_peak_hours | FLOAT8 | 17 / 17 | N/A | This is the current power usage during off peak hours in kwh | 
| off_peak_hours_returned | FLOAT8 | 17 / 17 | N/A | This is the returned power in off-peak hours to the electricity supplier in kwh | 
| current_power_returned | FLOAT8 | 17 / 17 | N/A | This is the power returned to the electricity supplier of the time of records in kwh | 

`Dim_Electricity_prices`: This is a dimension table that has the latest electricity prices available from the Dutch statistics bureau (CBS) with the following schema:
- `elec_prices_date_id`, `costperkwh`, `month`, `year`

| Field Name | Datatype | Field Length / Precision | Constraint | Description |
| --------------- | --------------- | --------------- | -------- | --------- |
| elec_prices_date_id | INT4 | 10 / 10 | NOT NULL PRIMARY KEY | This is the unique ID for each of the rows in the table |
| costperkwh | FLOAT8 | 10 / 10 | N/A | This is the cost per kwh in EUR |
| month | VARCHAR | 10 / 10 | N/A | This is the month for the cost per kwh |
| year | INT4 | 10 / 10 | N/A | This is year for the cost per kwh |

`Dim_Weather`: This is a dimension table that has all the weather data from the last 100 years in the Netherlands (popoulated in future release)
- `weather_date_id`, `temperature`, `month`, `year`

| Field Name | Datatype | Field Length / Precision | Constraint | Description |
| --------------- | --------------- | --------------- | -------- | --------- |
| weather_date_id | INT4 | 10 / 10 | NOT NULL PRIMARY KEY | This is the unique ID for each of the rows in the table |
| temperature | FLOAT8 | 10 / 10 | N/A | This is the temperature in CELCIUS degrees |
| month | VARCHAR | 10 / 10 | N/A | This is the month for temperature degrees |
| year | INT4 | 10 / 10 | N/A | This is the year for temperature degrees |

`Dim_Time`: This is a dimesion table that has timestamps of power usage broken down into specific units
- `date`, `datetime`, `week`, `hour`, `year`, `day of week`, `month`

| Field Name | Datatype | Field Length / Precision | Constraint | Description |
| --------------- | --------------- | --------------- | -------- | --------- |
| date | TIMESTMAP | 29 / 29 | NOT NULL / PRIMARY KEY | This is the unique timestamp for each row in the table |
| hour | INT4 | 10 /10 | N/A | This is the hour of the power usage dimension table |
| day | INT4 | 10 /10 | N/A | This is the day of the power usage dimension table | 
| week | INT4 | 10 /10 | N/A | This is the week of the power usage dimension table | 
| month | VARCHAR | 256 / 256 | N/A | This is the month of the power usage dimension table |
| year | INT4 | 10 /10 | N/A | This is the year of the power usage dimension table |
| weekday | VARCHAR | 256 / 256 | N/A | This is the day of the week of the power usage dimension table |

### Data model for DWH
![Schema for DWH](./schema.png)
