

import argparse
from flytekit.configuration import SerializationSettings, Config, PlatformConfig, SecretsConfig, AuthType, ImageConfig
from flytekit.remote import FlyteRemote
from uuid import uuid4

import mnist_training as wf1
import bayesian_optimization as wf2
import simple_example as wf3
import wine_classification as wf4

def register_all(remote):
    workflows = []
    workflows.append({"wf": wf1.mnist_workflow, "name": "mnist-training"})
    workflows.append({"wf": wf2.wf, "name": "bayesian_optimization"})
    workflows.append({"wf": wf3.wf, "name": "simple_example"})
    workflows.append({"wf": wf4.training_workflow, "name": "wine_classification"})

    version = str(uuid4())
    registered_workflows = []
    for workflow in workflows:
        image = f"ghcr.io/flyteorg/flytekit-python-template:{workflow['name']}-latest"
        print(f"Registering workflow: {workflow['name']} with image: {image}")
        reg_workflow = remote.register_workflow(
            entity = workflow["wf"],
            serialization_settings=SerializationSettings(image_config=ImageConfig.from_images(image),
                                                         project="flytetester",
                                                         domain="development"),
            version = version,
        )
        registered_workflows.append(reg_workflow)
    return registered_workflows

def execute_all(reg_workflows, remote):
    for reg_workflow in reg_workflows:
        execution = remote.execute(reg_workflow, inputs={})
        print(f"Execution url: {remote.generate_console_url(execution)}")
        completed_execution = remote.wait(execution)
        if completed_execution.error is not None:
            raise Exception(f"Execution failed with error: {completed_execution.error}")
        else:
            print(f"Execution succeeded: {completed_execution.outputs}")



if __name__ == "__main__":
    """
    This program takes a remote cluster, registers all templates on it - and then returns a url to the workflow on the Flyte Cluster.
        """
    args = argparse.ArgumentParser()
    args.add_argument("--host", type=str, required=True)
    args.add_argument("--insecure", type=bool, default=False)
    args.add_argument("--client_id", type=str, required=True)
    args.add_argument("--client_secret", type=str, required=True)
    args = args.parse_args()
    remote = FlyteRemote(
        config = Config(
            platform = PlatformConfig(
                endpoint = args.host,
                insecure = args.insecure,
                client_id = args.client_id,
                client_credentials_secret = args.client_secret,
                auth_mode = AuthType.CLIENT_CREDENTIALS,
        ),
            # secrets = SecretsConfig(default_dir="/etc/secrets"),
        )
    )

    remote_wfs = register_all(remote)
    print("All workflows Registered")
    execute_all(remote_wfs, remote)
    exit(0)