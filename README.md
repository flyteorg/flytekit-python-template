# flytekit-python-template
A template for the recommended layout of a Flyte enabled repository for code written in python using flytekit

## Usage
To get up and running with your Flyte project, we recommend proceeding through the following:

* Deploy the flyte sandbox locally or to any Kubernetes Cluster (EKS, GKE, custom, etc) by following the instructions at
   the [getting started guide](https://flyte.readthedocs.io/en/latest/administrator/install/getting_started.html#getting-started)
* Check the status of your [local deployment](http://localhost/console) and assert that it contains sample projects or
   in the case of a remote deployment enable port-forwarding
   
```shell
kubectl -n flyte port-forward svc/envoy 8001:80
```

and then verify you can access [localhost:8001/console](localhost:8001/console).

In the case of a remote deployment you'll need to enable port-forwarding to easily access your workflows and seamlessly register them,
in the case that the deployment endpoint is not publicly available.

Otherwise, access the remote deployment using ``http://<external-ip>/console``

* Register this template repo against your sandbox like so, substituting whichever host:port combination you are using:

```shell
FLYTE_HOST=localhost:80 make register_sandbox
```
