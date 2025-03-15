# Use AWS Lambda base image for Python
FROM public.ecr.aws/lambda/python:3.9

# Set working directory
WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files into the container
COPY src/ .

# Install dependencies
RUN pip install -r requirements.txt

# Command to start AWS Lambda with Flask
CMD ["server.lambda_handler"]
