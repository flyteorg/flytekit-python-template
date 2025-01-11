FROM python:3.10-slim-bookworm AS agent-slim

ARG VERSION

# Install required dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    prometheus-client \
    grpcio-health-checking==1.67.1

# Install Flytekit from GitHub
RUN pip install --no-cache-dir git+https://github.com/flyteorg/flytekit.git@master

# Copy and install the plugin
COPY flytekit-{{cookiecutter.project_name}} /{{cookiecutter.project_name}}
RUN pip install --no-cache-dir /flytekit-{{cookiecutter.project_name}}

# Cleanup
RUN apt-get purge -y build-essential git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set the default command
CMD ["pyflyte", "serve", "agent", "--port", "8000"]