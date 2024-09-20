# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables without default values
ENV RABBITMQ_HOST="localhost"
ENV RABBITMQ_PORT="5672"
ENV RABBITMQ_USER="admin"
ENV RABBITMQ_PASSWORD="admin"

# Command to run the FastAPI application
CMD ["python", "main.py"]