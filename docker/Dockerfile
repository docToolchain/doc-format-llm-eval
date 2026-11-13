# Sandbox image: one clean workspace per run, plus every format's validator.
ARG BASE_IMAGE=ruby:3.3-slim
FROM ${BASE_IMAGE}

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip git \
 && rm -rf /var/lib/apt/lists/*

RUN gem install asciidoctor -v 2.0.26

COPY docker/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY src /opt/docbench/src
COPY corpus /opt/docbench/corpus
COPY tasks /opt/docbench/tasks
ENV PYTHONPATH=/opt/docbench/src

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
