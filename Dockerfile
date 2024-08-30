# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the scripts folder into the /app/scripts directory
COPY scripts /app/scripts/
COPY requirements.txt /app/scripts/
COPY .env /app/scripts/

# Change the working directory to /app/scripts
WORKDIR /app/scripts

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run historical_data.py when the container launches. 
# We ensure the container stays running indefinitely, allowing us to execute commands in it as needed.
CMD ["sh", "-c", "python generate_data.py && python add_pks.py","tail", "-f", "/dev/null"]
