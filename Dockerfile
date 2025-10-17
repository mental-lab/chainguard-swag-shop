
FROM cgr.dev/chainguard-private/python:latest-dev
WORKDIR /app

# Copy pip configuration and authentication
COPY pip.conf /etc/pip.conf

ENV PIP_NO_INPUT=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NETRC=/home/nonroot/.netrc \
    VIRTUAL_ENV=/home/nonroot/.venv \
    PATH="/home/nonroot/.venv/bin:$PATH"

# Create venv and copy .netrc with proper permissions
RUN python3 -m venv "$VIRTUAL_ENV" && \
    mkdir -p /home/nonroot && \
    chown nonroot:nonroot /home/nonroot

# Copy .netrc as nonroot user
COPY --chown=nonroot:nonroot .netrc /home/nonroot/.netrc
RUN chmod 600 /home/nonroot/.netrc

COPY requirements.txt .

RUN pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt

# Force fresh install to ensure Chainguard packages are used
RUN pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt

COPY . .
EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "app.py"]
