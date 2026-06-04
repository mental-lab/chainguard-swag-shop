
# syntax=docker/dockerfile:1
FROM cgr.dev/packetloss.network/python:3.12-dev@sha256:bb4ee836294b76e62a31eda8e5a17857c525b2b45bd134d6767e372e754b94c8
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
    chown nonroot:nonroot /home/nonroot

COPY requirements.txt /tmp/requirements.txt

# Mount .netrc as a build secret (never baked into the image)
RUN --mount=type=secret,id=netrc,target=/home/nonroot/.netrc,uid=65532 \
    pip install --upgrade pip && \
    pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt

COPY . .
EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "app.py"]
