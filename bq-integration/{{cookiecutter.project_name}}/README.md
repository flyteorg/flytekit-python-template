# {{ cookiecutter.project_name }}

A template for the recommended layout of a Flyte enabled repository for code written in python using [flytekit](https://docs.flyte.org/projects/flytekit/en/latest/).
This particular template showcases how to interact with the [Flytekit BigQuery plugin](https://docs.flyte.org/projects/flytekit/en/latest/plugins/generated/flytekitplugins.bigquery.BigQueryTask.html) to enable access to GCPs Big Query service. 

## Usage

To get up and running with your Flyte project, we recommend following the
[Flyte getting started guide](https://docs.flyte.org/en/latest/getting_started.html).

This template requires the BigQuery backend plugin to be configured in your Flyte cluster. 
You will need to provide your ProjectID at runtime, associated with your GCP account.

## Imagespec

This template leverages Imagespec, check out the [ImageSpec Docs](..)
