# flytekit-python-template
A template for the recommended layout of a Flyte enabled repository for code written in python using flytekit

## Usage
To get up and running with your Flyte project, we recommend proceeding through the following:

1. Deploy the flyte sandbox locally by following the instructions at [getting started guide](https://flyte.readthedocs.io/en/latest/administrator/install/getting_started.html#getting-started)
1. Check the status of your [local deployment](http://localhost/console) and assert that it contains sample projects.
1. Register this template repo against your sandbox like so:

```shell
FLYTE_HOST=localhost:80 make register_sandbox
```
