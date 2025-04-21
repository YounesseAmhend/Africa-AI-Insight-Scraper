FROM python:3.12-alpine

# Set the working directory
WORKDIR /ai-insight-scraper

# Copy the requirements file and install Python dependencies
COPY requirements.txt .

ENV TZ=UTC

RUN pip install --no-cache-dir -r requirements.txt

# Ensure system dependencies for msedgedriver are installed
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libasound2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft Edge browser
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge.list && \
    apt-get update && \
    apt-get install -y microsoft-edge-stable && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application files
COPY . .

# Expose the necessary port
EXPOSE 50051

# Run the application
CMD ["python", "app.py"]
