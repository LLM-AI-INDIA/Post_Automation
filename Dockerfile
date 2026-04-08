# Use the official lightweight Python image.
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port (Cloud Run default is 8080, but Streamlit is flexible)
EXPOSE 8080

# Run the application
# Cloud Run injects a PORT environment variable. We use sh -c to ensure the variable is expanded.
# We set --server.port to $PORT (defaulting to 8080 if not set) and --server.address to 0.0.0.0
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]
