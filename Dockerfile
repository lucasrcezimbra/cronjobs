FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip && pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --without=dev

COPY . /app
