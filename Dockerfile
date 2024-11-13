# Base image
FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    g++ \
    imagemagick \ 
    ffmpeg \
    default-jdk \
    && apt-get clean
# Set the working directory inside the container
ENV JAVA_HOME /usr/lib/jvm/java-1.7-openjdk/jre

WORKDIR /app/


COPY ./requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./download_models.py /app/download_models.py
RUN python download_models.py
COPY . /app/


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#ENV TRANSFORMERS_CACHE /app/.cache/


# Command to run your application
CMD ["gradio", "app.py"]
