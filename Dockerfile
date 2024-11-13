# Base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file (if available) and other files
COPY requirements.txt ./
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Gradio will run on
EXPOSE 7860

# Command to run your application
CMD ["python", "app.py"]
