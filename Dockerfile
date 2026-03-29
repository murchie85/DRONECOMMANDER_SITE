# Use a lightweight Python Linux image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install Gunicorn (The Production Server)
RUN pip install gunicorn

# Copy the rest of the app code
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the app using Gunicorn
# -w 4: Use 4 worker processes (scaling!)
# -b: Bind to port 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "app:app"]