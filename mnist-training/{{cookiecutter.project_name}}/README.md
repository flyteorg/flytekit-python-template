# {{ cookiecutter.project_name }}

A template that provides an end-to-end example of how to use Flyte to train a model on the MNIST dataset.
This uses the Pytorch package built for versoin 2.0
## Usage

To get up and running with your Flyte project, we recommend following the
[Flyte getting started guide](https://docs.flyte.org/en/latest/getting_started.html).

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

We recommend using a git repository to version this project, so that you can
use the git sha to version your Flyte workflows.

## To execute
To run the example we recommend either using a [local k3s cluster](https://docs.flyte.org/projects/flytectl/en/latest/gen/flytectl_demo_start.html), 
or using a hosted kubernetes cluster.

### Default Image
To make things easy, we created a default public OCI image that you can use to run this tutorial, it can be found here:
```ghcr.io/flyteorg/flytekit-python-templates:mnist-training-latest```

### Pyflyte Run
```bash
pyflyte run --remote --image ghcr.io/flyteorg/flytekit-python-templates:mnist-training-latest --n_epoch 100 --gpu_enabled
```


### Pyflyte Register
Or you can register the workflow and launch it from the Flyte console.
```bash
pyflyte register workflows -p flytesnacks -d development --image ghcr.io/flyteorg/flytekit-python-templates:mnist-latest
```
