# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=docker.io/library/debian:stable-slim
FROM $BASE_IMAGE AS base
USER root
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes libcairo2 python3 && \
    rm -rf /var/lib/apt/lists/*

FROM base AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes git python3-venv && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m venv /app && \
    /app/bin/pip install --upgrade uv

COPY pyproject.toml /build/pyproject.toml
RUN VIRTUAL_ENV=/app /app/bin/uv pip install -r /build/pyproject.toml && \
    XDG_CACHE_HOME=/cache /app/bin/python -c 'import capellambse_context_diagrams as ccd; ccd.install_elk()'

COPY .git /build/.git
COPY README.md /build
COPY capella2polarion /build/capella2polarion
RUN VIRTUAL_ENV=/app /app/bin/uv pip install /build

FROM base
ARG RUNTIME_USER=root
ENV VIRTUAL_ENV=/app
ENV PATH=/app/bin:/usr/local/bin:/usr/bin:/bin
ENV XDG_CACHE_HOME=/cache
COPY --from=build /app /app
COPY --from=build /cache /cache
RUN install -d -o "$RUNTIME_USER" -m 700 /cache/capellambse
USER $RUNTIME_USER
ENTRYPOINT ["capella2polarion"]
