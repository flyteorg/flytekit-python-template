import argparse
import sys, os, json
from flytekit.configuration import SerializationSettings, Config, PlatformConfig, SecretsConfig, AuthType, ImageConfig
from flytekit.core.base_task import PythonTask
from flytekit.core.workflow import WorkflowBase
from flytekit.remote import FlyteRemote
from uuid import uuid4
from contextlib import contextmanager

root_directory = os.path.abspath(os.path.dirname(__file__))


@contextmanager
def workflows_module_management(workflow_name):
    """
    allows for the import of a workflow module from a path,
    but imports from the templates root directory; preserving the correct path for imports
    """
    module_name = "workflows"
    path = os.path.join(root_directory, workflow_name, "{{cookiecutter.project_name}}")
    sys.path.insert(0, path)
    try:
        yield __import__(module_name)
    finally:
        sys.path.remove(path)
        for name in dir(sys.modules[module_name]):
            if name.startswith('__'):
                continue

            if name in globals():
                del globals()[name]
        if module_name in sys.modules:
            del sys.modules[module_name]


def register_all(remote, templates, image_suffix):

    version = str(uuid4())
    registered_workflows = []
    for template_name in templates:
        with workflows_module_management(template_name) as wf_module:
            print(wf_module.wf.name)
            image = f"ghcr.io/flyteorg/flytekit-python-template:{template_name}-{image_suffix}"
            print(f"Registering workflow: {template_name} with image: {image}")
            if isinstance(wf_module.wf, WorkflowBase):
                reg_workflow = remote.register_workflow(
                    entity=wf_module.wf,
                    serialization_settings=SerializationSettings(image_config=ImageConfig.from_images(image),
                                                                 project="flytetester",
                                                                 domain="development"),
                    version=version,
                )
            elif isinstance(wf_module.wf, PythonTask):
                reg_workflow = remote.register_task(
                    entity=wf_module.wf,
                    serialization_settings=SerializationSettings(image_config=ImageConfig.from_images(image),
                                                                 project="flytetester",
                                                                 domain="development"),
                    version=version,
                )
            else:
                raise Exception("Unknown workflow type")
            print(f"Registered workflow: {template_name}")
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
    args.add_argument("--image_suffix", type=str, default="latest")
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
        )
    )

    with open('templates.json') as f:
        templates_list = json.load(f)

    remote_wfs = register_all(remote, templates_list, args.image_suffix)
    print("All workflows Registered")
    execute_all(remote_wfs, remote)
    exit(0)
