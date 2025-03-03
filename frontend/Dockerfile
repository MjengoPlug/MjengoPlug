# frontend/Dockerfile

# Use the official Node.js 22 image based on Debian Bullseye
FROM node:22-bullseye-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the frontend files into the container
COPY frontend/ /app/

# Install the dependencies
RUN npm install

# Expose the port your frontend will run on
EXPOSE 3000

# Command to run the application
CMD ["npm", "run", "dev"]
