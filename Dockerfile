# Use an official Python runtime as the base image
FROM python:3.8-slim


ENV PYTHONUNBUFFERED=True

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory (our Flask app) into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y wget && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    apt-get remove -y wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the FLASK_APP environment variable
ENV FLASK_APP=src/app.py


# Make port 5000 available for the app
EXPOSE 5000

# Run the command to start the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]