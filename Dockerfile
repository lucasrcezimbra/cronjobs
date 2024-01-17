# Rust is required to install cryptography when running on a Rasbperry PI
FROM rust:latest

RUN apt-get update && apt-get install -y python3-dev pipx && pipx install poetry
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --without=dev

COPY . /app
