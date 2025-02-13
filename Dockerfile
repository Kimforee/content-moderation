# Use official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Generate/update poetry.lock and install dependencies
RUN poetry lock && poetry install

COPY . /app

# Expose port
EXPOSE 8000

# Run the application
CMD poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000