FROM python:3.12-slim

LABEL maintainer="Manav Khandurie <manavkhandurie@gmail.com>"

# Set the safe location for your action's code
WORKDIR /opt/bot

# Copy your poetry files
COPY pyproject.toml poetry.lock* /opt/bot/

# Install system deps
RUN apt-get update && apt-get install -y git curl && apt-get clean

# Install Python deps
RUN pip install --upgrade pip
RUN pip install poetry poetry-plugin-export

# Export only production dependencies (no dev, no hashes)
RUN poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt && cat requirements.txt 
RUN pip install -r requirements.txt

# Copy the full bot source code to safe location
COPY . /opt/bot/

# Final entrypoint - run your script from safe location
ENTRYPOINT ["python", "/opt/bot/entrypoint.py"]
