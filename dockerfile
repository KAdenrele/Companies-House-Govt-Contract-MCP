# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Install poppler-utils
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

EXPOSE 50000
# Command to run the application
CMD ["python3", "server.py"]

