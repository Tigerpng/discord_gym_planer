# syntax=docker/dockerfile:1

# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir discord.py \
    && pip install --no-cache-dir python-dotenv \
    && pip install --no-cache-dir sqlobject

# Copy project files
COPY . /app

# Start the bot
CMD ["python3", "main.py"]