This is the data collection microservice as an API which is part of our application.
The real purpose of this microservice is to collect data from 3rd party APIs such as NewsAPI and Alphavantage.
It then cleans and formats the data returned from the APIs mentioned.
One the Data has been formated to the ADAGE 3.0 standards, it is to be stored in our database.

![Pipeline](https://github.com/pokemon47/Qubit_data_collection/actions/workflows/data-collection-ci.yml/badge.svg)

[![Data Collection Testing Report](https://img.shields.io/badge/Artifact-Download-blue)](https://github.com/pokemon47/Qubit_data_collection/actions/runs/${GITHUB_RUN_ID}/artifacts/data-collection-testing-report)
