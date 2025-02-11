# Use official Python image
FROM python:3.12.2-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
