"""Basic Union BYOC workflow template."""

from unionai import task, workflow, ImageSpec

# ImageSpec defines the container image used for the Kubernetes pods that run the tasks in Union.
image_spec = ImageSpec(

    # The name of the image
    name="basic-union-byoc-image",

    # The base image on which this image is based
    base_image="ghcr.io/flyteorg/flytekit:py3.11-latest",

    # Use the requirements.txt to define the packages to be installed in the the image
    requirements="requirements.txt",

    # Container registry to which the image will be pushed.
    # Make sure that:
    # * You subsitutue the actual name of the registry here.
    #   If you are using GHCR, substitute <my-github-org> with your github org name.
    # * You have Docker installed locally and are logged into this registry.
    # * The image, once pushed to the registry, is accessible to Union
    #   (for example, for GHCR, make sure the image is public)
    #
    # Only needed for BYOC.
    # On Serverless, images are stored in Union's own container registry.
    registry="ghcr.io/<my-github-org>"

    # Python version of the image. Use default python in the base image if None.
    # python_version="3.11"

    # Plugin used to build the image locally.
    # Uses flytekitplugin_envd by default.
    #
    # Only applies to BYOC.
    # On Serverless, Images are built by Union's ImageBuilder service.
    # builder="flytekitplugins_envd"

    # Source root of the image.
    # source_root="/path/to/source/root"

    # Environment variables to be set in the image.
    # env=[FOO="foo", BAR="bar"]

    # List of python packages to install.
    # packages=["package-1", "package-2"]

    # List of conda packages to install.
    # conda_packages=["package-1", "package-2"]

    # List of conda channels.
    # conda_channels=["channel-1", "channel-2"]

    # List of apt packages to install.
    # apt_packages=["package-1", "package-2"]

    # Version of cuda to install.
    # cuda="12.5"

    # Version of cudnn to install.
    # cudnn="9.2.0"

    # Target platforms for the build output
    # (for example: windows/amd64, linux/amd64, darwin/arm64)
    # platform=["linux/amd64"]

    # Custom pip index url
    # pip_index="https://my-pypi.mywebsite.com/simple"

    # One or more pip index urls as a list
    # pip_extra_index_url=["https://my-pypi.mywebsite.com/simple", "https://my-other-pypi.mywebsite.com/simple"]

    # Path to a JSON registry config file
    # registry_config ="/path/to/registry/config.json"

    # Commands to run during the build process
    # commands= ["pip install -r requirements.txt"]

    # Custom string format for image tag. The ImageSpec hash is passed in as `spec_hash`.
    # So, for example, to add a "dev" suffix to the image tag use:
    # tag_format = "{spec_hash}-dev"
)

@task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"


@workflow
def wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
