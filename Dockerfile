# syntax=docker/dockerfile:1
# Chainguard OS: hardened, minimal Python image. Public for the demo; swap
# to cgr.dev/vulnfreeish.dev/python (Custom Assembly) once entitled.
# Note: no shell, no apt — the netrc build secret carries Libraries auth.
FROM cgr.dev/chainguard/python:latest-dev
WORKDIR /app

# Copy pip configuration
COPY pip.conf /etc/pip.conf

ENV PIP_NO_INPUT=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/home/nonroot/.venv \
    PATH="/home/nonroot/.venv/bin:$PATH"

# Create venv
RUN python3 -m venv "$VIRTUAL_ENV" && \
    mkdir -p /home/nonroot && \
    chown 65532:65532 /home/nonroot

COPY requirements.txt /tmp/requirements.txt

# Mount .netrc as a build secret (never baked into the image)
RUN --mount=type=secret,id=netrc,target=/home/nonroot/.netrc,uid=65532 \
    pip install --upgrade pip && \
    pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt

COPY . .
EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "app.py"]
