# Use an official Python runtime as the base image
# FROM python:3.10
FROM --platform=linux/amd64 python:3.10-slim-buster as build

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port on which the Flask app will run (default is 5000)
EXPOSE 5000

# Specify the command to run your Flask app using a production server (e.g., Gunicorn)
# CMD ["uwsgi", "--bind", "0.0.0.0:5000", "whatsapp_processor:app"]

# CMD ["python", "whatsapp_processor.py"]

CMD ["uwsgi", "--socket", "0.0.0.0:5000", "--protocol=http", "-w", "whatsapp_processor:app"]
