import pandas as pd
from flytekit import dynamic, workflow, ImageSpec
from flytekitplugins.bigquery import BigQueryConfig, BigQueryTask

"""
Workflow that showcases how a big query request can be made against a public big query dataset.
This workflow requires a ProjectID and for the flyte role to have big query read/write access within your organization.
Utilizes ImageSpec to 
"""


"""
Change the registry to point to your own image registry (ghcr.io or otherwise such as docker).

"""
spec = ImageSpec(
    name="flytekit",
    packages=["flytekitplugins-bigquery==1.6.1"],
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    registry=" ghcr.io/unionai-oss"
)


def create_bigquery_task(project_id: str, query_command: str) -> BigQueryTask:
    return BigQueryTask(
        name="sql.bigquery.no_io",
        output_structured_dataset_type=pd.DataFrame,
        query_template=query_command,
        task_config=BigQueryConfig(ProjectID=project_id))

@dynamic(container_image=spec)
def execute_bigquery_query(project_id: str, query_command: str) -> pd.DataFrame:
    bigquery_task = create_bigquery_task(project_id=project_id, query_command=query_command)
    return bigquery_task()


@workflow
def execute_bigquery_wf(project_id: str) -> pd.DataFrame:
    query_command: str = "SELECT * FROM  `bigquery-public-data.google_trends.top_terms` limit 10"
    return execute_bigquery_query(project_id=project_id, query_command=query_command)

