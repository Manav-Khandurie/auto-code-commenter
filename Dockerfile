FROM python:3.10-slim

LABEL maintainer="Manav Khandurie <manavkhandurie@gmail.com>"

RUN apt-get update && apt-get install -y git curl && apt-get clean

RUN pip install --upgrade pip
RUN pip install poetry poetry-plugin-export

# Export only production dependencies (no dev, no hashes)
RUN poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt

WORKDIR /bot

COPY pyproject.toml poetry.lock* /bot/

COPY . /bot/

ENTRYPOINT ["python", "entrypoint.py"]
