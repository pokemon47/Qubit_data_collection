# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies (including Flask) specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for API keys (or use defaults if not set)
ENV FLASK_APP=src.server
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose port 5000 for Flask to run on
EXPOSE 5000

# Set the default command to run the Flask app (assuming server.py starts it)
CMD ["python", "src/server.py"]
