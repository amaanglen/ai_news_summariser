# Use a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose the port that Flask runs on
EXPOSE 5000

# Set environment variable for Flask to run in development mode
ENV FLASK_APP=app.py
# ENV FLASK_ENV=development

# Run the Flask app when the container starts
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
