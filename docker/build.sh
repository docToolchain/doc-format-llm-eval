#!/usr/bin/env bash
# Build the sandbox image. Extra arguments go to `docker build`,
# e.g. --network host --build-arg BASE_IMAGE=my-mirror/ruby:3.3-slim
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -f docker/Dockerfile -t docbench-sandbox:latest "$@" .
