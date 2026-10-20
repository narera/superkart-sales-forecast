# Lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container's working directory
COPY . .

# Install dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Document the port the API listens on
EXPOSE 7860

# Start the API with Gunicorn:
# - `-w 4`: 4 worker processes to handle requests in parallel
# - `-b 0.0.0.0:7860`: listen on port 7860 on all network interfaces
# - `app:superkart_api`: the Flask instance named `superkart_api` inside app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
