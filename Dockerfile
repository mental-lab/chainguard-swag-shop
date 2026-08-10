# syntax=docker/dockerfile:1
# Chainguard OS: the org's Custom Assembly Python image. Floating `latest`
# on purpose — every CI run compares the *current* upstream baseline against
# the *current* Chainguard image, so the diff never goes stale.
# Multi-stage: the runtime image has no shell, so deps are built in the
# -dev variant and the venv is copied into the minimal runtime image.
FROM cgr.dev/vulnfreeish.dev/python:latest-dev AS builder
WORKDIR /app

USER root

# Copy pip configuration
COPY pip.conf /etc/pip.conf

ENV PIP_NO_INPUT=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/home/nonroot/.venv \
    PATH="/home/nonroot/.venv/bin:$PATH"

# Create venv
RUN python3 -m venv "$VIRTUAL_ENV" && \
    mkdir -p /home/nonroot

COPY requirements.txt /tmp/requirements.txt

# Mount .netrc as a build secret (never baked into the image)
RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    pip install --upgrade pip && \
    pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt && \
    chown -R 65532:65532 /home/nonroot

FROM cgr.dev/vulnfreeish.dev/python:latest
WORKDIR /app

ENV PIP_NO_INPUT=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/home/nonroot/.venv \
    PATH="/home/nonroot/.venv/bin:$PATH"

COPY --from=builder --chown=65532:65532 /home/nonroot/.venv /home/nonroot/.venv
COPY . .
EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "app.py"]
