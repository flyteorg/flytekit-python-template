import argparse
import sys, os
from flytekit.configuration import SerializationSettings, Config, PlatformConfig, SecretsConfig, AuthType, ImageConfig
from flytekit.core.base_task import PythonTask
from flytekit.core.workflow import WorkflowBase
from flytekit.remote import FlyteRemote
from uuid import uuid4

root_directory = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(root_directory, "simple-example"))
import workflows_simple as wf1

sys.path.append(os.path.join(root_directory, "mnist-training"))
import workflows_mnist as wf2

sys.path.append(os.path.join(root_directory, "bayesian-optimization"))
import workflows_bayesian as wf3

sys.path.append(os.path.join(root_directory, "wine-classification"))
import workflows_wine as wf4


def register_all(remote):
    workflows = []
    workflows.append({"wf": wf3.wf, "name": "simple-example"})
    workflows.append({"wf": wf1.mnist_workflow, "name": "mnist-training"})
    workflows.append({"wf": wf2.wf, "name": "bayesian-optimization"})
    workflows.append({"wf": wf4.training_workflow, "name": "wine-classification"})

    version = str(uuid4())
    registered_workflows = []
    for workflow in workflows:
        image = f"ghcr.io/flyteorg/flytekit-python-template:{workflow['name']}-latest"
        print(f"Registering workflow: {workflow['name']} with image: {image}")
        if isinstance(workflow["wf"], WorkflowBase):
            reg_workflow = remote.register_workflow(
                entity=workflow["wf"],
                serialization_settings=SerializationSettings(image_config=ImageConfig.from_images(image),
                                                             project="flytetester",
                                                             domain="development"),
                version=version,
            )
        elif isinstance(workflow["wf"], PythonTask):
            reg_workflow = remote.register_task(
                entity=workflow["wf"],
                serialization_settings=SerializationSettings(image_config=ImageConfig.from_images(image),
                                                             project="flytetester",
                                                             domain="development"),
                version=version,
            )
        else:
            raise Exception("Unknown workflow type")
        print(f"Registered workflow: {workflow['name']}")
        registered_workflows.append(reg_workflow)
    return registered_workflows


def execute_all(reg_workflows, remote):
    for reg_workflow in reg_workflows:
        print(f"Executing workflow: {reg_workflow.id}")
        execution = remote.execute(reg_workflow, inputs={}, project="flytetester", domain="development")
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
        config=Config(
            platform=PlatformConfig(
                endpoint=args.host,
                insecure=args.insecure,
                client_id=args.client_id,
                client_credentials_secret=args.client_secret,
                auth_mode=AuthType.CLIENT_CREDENTIALS,
            ),
            # secrets = SecretsConfig(default_dir="/etc/secrets"),
        )
    )

    remote_wfs = register_all(remote)
    print("All workflows_bayesian Registered")
    execute_all(remote_wfs, remote)
    exit(0)
