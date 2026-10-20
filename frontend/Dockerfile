# Use a minimal base image with Python installed
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the current directory on the host to the container's /app directory
COPY . .

# Install Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Document the port Streamlit listens on
EXPOSE 8501

# Run the Streamlit app on port 8501 and make it accessible from outside the container.
# XSRF protection and CORS are disabled so file uploads work through the Codespaces port-forwarding proxy.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
