FROM python:3.11.8-slim-bookworm

ENV PATH /usr/local/bin:$PATH
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libpq-dev \
#    libssl-dev \
#    libffi-dev \
#    python3-dev \
#    python3-pip \
#    python3-setuptools \
#    python3-wheel

RUN set -ex apt-get autoremove -y
RUN    apt-get clean -y
RUN    rm -rf /var/lib/apt/lists/*


ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip


RUN pip3 install poetry
WORKDIR /app

COPY ./poetry.lock ./pyproject.toml /app/

RUN poetry config virtualenvs.in-project false
RUN poetry export --without-hashes --format=requirements.txt > requirements.txt
RUN pip install -r requirements.txt


#FROM python:3.11.8-slim-bookworm as app
#WORKDIR /app
#COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY ./ /app/

ENV PYTHONPATH=/app
RUN addgroup --system --gid 1001 app
RUN adduser --system --uid 1001 --gid 1001 --no-create-home app
USER app

ENTRYPOINT ["python", "run.py"]
EXPOSE 6677


