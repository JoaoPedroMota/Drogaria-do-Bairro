# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    pip install psycopg2

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install -r requirements.txt

# Expose port 8000 for the Django application
EXPOSE 8080

# Run the command to start the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
