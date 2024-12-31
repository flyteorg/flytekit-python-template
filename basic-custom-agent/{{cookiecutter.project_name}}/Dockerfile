FROM python:3.10-slim-bookworm

MAINTAINER Flyte Team <users@flyte.org>
LABEL org.opencontainers.image.source=https://github.com/flyteorg/flytekit

# additional dependencies for running in k8s
RUN pip install prometheus-client grpcio-health-checking
# flytekit will autoload the agent if package is installed.
RUN pip install flytekitplugins-bigquery
CMD pyflyte serve agent --port 8000