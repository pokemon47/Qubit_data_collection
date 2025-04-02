# Qubit Data Collection
This is the data collection microservice as an API which is part of our application.
The real purpose of this microservice is to collect data from 3rd party APIs such as NewsAPI and Alphavantage.
It then cleans and formats the data returned from the APIs mentioned.
One the Data has been formated to the ADAGE 3.0 standards, it is to be stored in our database.

![Pipeline](https://github.com/pokemon47/Qubit_data_collection/actions/workflows/data-collection-ci.yml/badge.svg)

## Testing Report

To download the latest testing report PDF, go to the "Actions" tab of the
repository, click on the latest workflow run, and scroll down to Artifacts.

The testing report PDF should be contained inside the artifact file named
**data-collection-testing-report**. The other artifact files contain incomplete
data from various jobs in the pipeline.
