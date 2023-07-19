In this repository you'll find a collection of [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) templates for making [Flyte](https://github.com/flyteorg/flyte) projects.

We use cookiecutter's ability to define [multiple templates to be defined in the same repository](https://cookiecutter.readthedocs.io/en/latest/advanced/directories.html). Each cookiecutter template is defined in a separate directory, e.g. the template used in Flyte's [Getting Started](https://docs.flyte.org/en/latest/getting_started.html) guide lives in a directory called `simple-example`.

This project includes a script `docker_build.sh` that you can use to build a
Docker image for your Flyte project.

```
# help
./docker_build.sh -h

# build an image with defaults
./docker_build.sh

# build an image with custom values
./docker_build.sh -p {{ cookiecutter.project_name }} -r <REGISTRY> -v <VERSION>
```

## Images
Compiled Images for all templates can be found in our [ghcr.io registry](https://github.com/flyteorg/flytekit-python-template/pkgs/container/flytekit-python-template)

## Usage

Each template can be rendered by specifying the `--directory` flag to cookiecutter. For example, in order to generate a project using the `simple-example` template run:

    $ cookiecutter https://github.com/flyteorg/flytekit-python-template.git --directory="simple-example"

This should prompt for a few variables that will be used to setup the project.
