# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the Docker container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY dependencies.txt .

# Install the python dependencies
RUN pip install --no-cache-dir -r dependencies.txt

# Copy the Flask app to the container
COPY orchestrator.py .

# Expose the port the app will run on
EXPOSE 8000

# Command to run the Flask app
CMD ["python", "./orchestrator.py"]




