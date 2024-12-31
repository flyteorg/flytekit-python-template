# flyte-custom-agent-template
How to write your custom agent and build it with a Dockerfile.

## Concepts
1. flytekit will load plugin [here](https://github.com/flyteorg/flytekit/blob/ff2d0da686c82266db4dbf764a009896cf062349/flytekit/__init__.py#L322-L323), 
so you must add your plugin to `entry_points` in [setup.py](https://github.com/Future-Outlier/flyte-custom-agent-template/blob/main/flytekit-bigquery/setup.py#L39).
2. Agent registration is triggered by loading the plugin. For example,
BigQuery's agent registration is triggered [here](https://github.com/Future-Outlier/flyte-custom-agent/blob/main/flytekit-bigquery/flytekitplugins/bigquery/agent.py#L97)

## Build your custom agent
1. Following the folder structure in this repo, you can build your custom agent.
2. Build your own custom agent ([learn more](https://docs.flyte.org/en/latest/user_guide/flyte_agents/developing_agents.html))

> In the following command, `localhost:30000` is the Docker registry that ships with the Flyte demo cluster. Use it or replace it with a registry where you have push permissions.

```bash
docker buildx build --platform linux/amd64 -t localhost:30000/flyteagent:custom-bigquery -f Dockerfile .
```

3. Test the image:
```bash
docker run -it localhost:30000/flyteagent:custom-bigquery
```

4. Check the logs (sensor is created by flytekit, bigquery is created by the custom agent)
```
(dev) future@outlier ~ % docker run -it localhost:30000/flyteagent:custom-bigquery
    
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
🚀 Starting the agent service...
Starting up the server to expose the prometheus metrics...
                       Agent Metadata                       
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Agent Name     ┃ Support Task Types            ┃ Is Sync ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Sensor         │ sensor (v0)                   │ False   │
│ Bigquery Agent │ bigquery_query_job_task (v0)  │ False   │
└────────────────┴───────────────────────────────┴─────────┘
```