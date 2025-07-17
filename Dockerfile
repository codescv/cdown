# Use a slim Python base image
FROM python:3.10-slim

# Install git (required for git installs) and uv
RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Install the cdown tool from the specified GitHub repository.
# For production, you can pin this to a specific commit or tag, e.g.:
# RUN uv tool install git+https://github.com/codescv/cdown.git@v0.1.0
RUN uv tool install git+https://github.com/codescv/cdown.git

# The entrypoint is the path where `uv` installs the tool.
ENTRYPOINT ["/root/.local/bin/cdown"]

