FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Run Django server
CMD ["python", "ws_project_1/manage.py", "runserver", "0.0.0.0:8000"]
