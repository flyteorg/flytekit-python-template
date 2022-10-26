# {{ cookiecutter.project_name }}

A template for with the recommended layout of a Flyte enabled repository for code written
in python using [flytekit](https://docs.flyte.org/projects/flytekit/en/latest/).
The `workflows` directory contains an example of how to do bayesian optimization with
Flyte using the `bayesian-optimization` library.

## Usage

To get up and running with your Flyte project, we recommend following the
[Flyte getting started guide](https://docs.flyte.org/en/latest/getting_started.html)


## NOTE
1. This APP name is also added to ``docker_build_and_tag.sh`` - ``APP_NAME``
2. We recommend using a git repository and this the ``docker_build_and_tag.sh``
   to build your docker images
3. We also recommend using pip-compile to build your requirements.
