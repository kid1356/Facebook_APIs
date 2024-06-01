FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=facebook.settings

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    python3-dev \
    libressl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    zlib-dev \
    && rm -rf /var/cache/apk/*

# Create and set the working directory
RUN mkdir /facebook
WORKDIR /facebook

# Copy the application code to the container
COPY . /facebook//

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /facebook//
RUN pip install -r requirements.txt

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
