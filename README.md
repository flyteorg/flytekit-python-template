# flytekit-python-template

A template for the recommended layout of a Flyte enabled repository for code written in python using flytekit

## Usage

To get up and running with your Flyte project, we recommend proceeding through the following:

* Deploy the flyte sandbox locally or to any Kubernetes Cluster (EKS, GKE, custom, etc) by following the instructions at the [getting started guide](https://docs.flyte.org/en/latest/getting_started.html)
* Check the status of your [local deployment](http://localhost:30081/console) and assert that it contains sample projects or in the case of a remote deployment enable port-forwarding
   
```shell
kubectl -n flyte port-forward svc/envoy 8001:80
```

and then verify you can access [localhost:30081/console](localhost:30081/console).

In the case of a remote deployment you'll need to enable port-forwarding to easily access your workflows and seamlessly register them, in the case that the deployment endpoint is not publicly available.

Otherwise, access the remote deployment using ``http://<external-ip>/console``

* Register this template repo against your Flyte deployment like so, substituting whichever host:port combination you are using:

```shell
FLYTE_HOST=<host>:<port> make register
```
