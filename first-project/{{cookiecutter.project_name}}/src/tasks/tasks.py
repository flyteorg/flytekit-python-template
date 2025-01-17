"""Tasks"""

import union

image_spec = union.ImageSpec(

    # The name of the image.
    name="first-project-image",

    # Use the `uv.lock` file in this project to define the dependencies included in the image.
    requirements="uv.lock",

    # The container registry to which the image will be pushed.
    # Only used for Union BYOC. Not used for Union Serverless
    # Uncomment this parameter if you are using Union BYOC.:
    #
    # * Substitute the actual name of the registry for <my-registry>.
    #   (for example if you are using GitHub's GHCR, you would use "ghcr.io/<my-github-org>").
    #
    # * Make sure you have Docker installed locally and are logged into that registry.
    #
    # * Make sure that the image, once pushed to the registry, is accessible to Union
    #   (for example, for GHCR, make sure the image is public).
    #
    # registry="<my-registry>"
)

@union.task(container_image=image_spec)
def task_1(name: str) -> str:
    return f"Hello, {name}!"
