In this repository you'll find a collection of [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) templates for making [Flyte](https://github.com/flyteorg/flyte) projects.

We use cookiecutter's ability to define [multiple templates to be defined in the same repository](https://cookiecutter.readthedocs.io/en/latest/advanced/directories.html). Each cookiecutter template is defined in a separate directory, e.g. the template used in Flyte's [Getting Started](https://docs.flyte.org/en/latest/getting_started.html) guide lives in a directory called `basic-template-imagespec`.

## Images

Compiled images for all templates can be found in our [ghcr.io registry](https://github.com/flyteorg/flytekit-python-template/pkgs/container/flytekit-python-template)

### ImageSpec vs Dockerfile

Flytekit uses the `basic-template-imagespec` template by default when you initialize a new project with `pyflyte init`. That template uses [ImageSpec](https://docs.flyte.org/en/latest/user_guide/customizing_dependencies/imagespec.html), which builds Docker images without a Dockerfile, so doesn't contain a Dockerfile or `docker-build.sh` script.

However, some templates in this repository contain a Dockerfile and `docker-build.sh` script that you can use to build a Docker image for your Flyte project:

```
# help
./docker_build.sh -h

# build an image with defaults
./docker_build.sh

# build an image with custom values
./docker_build.sh -p {{ cookiecutter.project_name }} -r <REGISTRY> -v <VERSION>
```

**Note:** You should only use `docker-build.sh` script to build a Docker image for a Flyte project that contains a Dockerfile.

## Usage

Each template can be rendered by specifying the `--directory` flag to cookiecutter. For example, in order to generate a project using the `basic-template-imagespec` template, run:

    $ cookiecutter https://github.com/flyteorg/flytekit-python-template.git --directory="basic-template-imagespec"

This should prompt for a few variables that will be used to set up the project.
