# flytekit-python-template

A template for the recommended layout of a Flyte enabled repository for code written in python using [flytekit](https://docs.flyte.org/projects/flytekit/en/latest/)

## Usage

To get up and running with your Flyte project, we recommend following the
[Flyte getting started guide](https://docs.flyte.org/en/latest/getting_started.html)


## NOTE
1. Once you have acquainted yourself, update the root package name from ``myapp`` -> ``your actual appnamee``
2. This APP name is also added to ``docker_build_and_tag.sh`` - ``APP_NAME``
3. We recommend using a git repository and this the ``docker_build_and_tag.sh``
   to build your docker images
4. We also recommend using pip-compile to build your requirements.
