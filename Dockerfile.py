# Use a dedicated Python image
FROM python:3.11-slim

# Set a working directory (best practice)
WORKDIR /app

# Copy your files
COPY main.py .
COPY books/ books/

# Run your script
CMD ["python", "main.py"]