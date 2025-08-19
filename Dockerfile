# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=docker.io/library/debian:stable-slim
FROM $BASE_IMAGE AS base
USER root
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes libcairo2 python3

FROM base AS build
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes git python3-venv && \
    python3 -m venv /app && \
    /app/bin/pip install --upgrade uv

COPY pyproject.toml /build/pyproject.toml
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    VIRTUAL_ENV=/app /app/bin/uv pip install -r /build/pyproject.toml && \
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
