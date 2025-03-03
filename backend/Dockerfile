# # backend/Dockerfile

# # Use an official Python runtime as a parent image
# FROM python:3.9-slim

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the backend files into the container
# COPY backend/ /app/

# # Install any needed dependencies
# RUN pip install --upgrade pip
# RUN pip install -r /app/backend/requirements.txt

# # Expose the port your backend will run on (change it to your backend's port)
# EXPOSE 8000

# # Set environment variables (optional)
# ENV PYTHONUNBUFFERED 1

# # Command to run the application (replace with your actual run command)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



# Use the official Python 3.13 image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend files into the container
COPY backend/ /app/

# Install any needed dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/backend/requirements.txt

# Expose the port your backend will run on
EXPOSE 8000

# Set environment variables (optional)
ENV PYTHONUNBUFFERED 1

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
