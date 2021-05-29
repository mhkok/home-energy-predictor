# home-energy-predictor

## Introduction
This project retrieves data from your smart meter and pushes into dwh for analysis, combined with several external data sources like weather, weather forecasts and electricity prices. 


## Architecture
The architecture of the Home Energy Predictor consists of a myriad of technologies. Streaming data is being collected from your Raspberry Pi through a P1 cable into the cloud (S3 blob storage). On a daily basis an Airflow data pipeline is run to push the data into AWS Redshift. In order to be able to predict your energy usage & costs based on external factors like weather, weather forecasts several different data sources are imported into AWS Redsfhift using Airflow.

![Airflow Data pipeline](./architecture.png)

## Data types & files




## Schema for DWH

![Schema for DWH](./schema.png)