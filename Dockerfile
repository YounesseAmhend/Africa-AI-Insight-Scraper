FROM python:3.12-slim

# Set up the working directory
WORKDIR /app

# Install prerequisites and Microsoft Edge in a single layer
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    apt-transport-https \
    unzip \
    --no-install-recommends \
    && wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list \
    && apt-get update \
    && apt-get install -y microsoft-edge-dev \
    && EDGE_VERSION=$(microsoft-edge --version | awk '{print $3}') \
    && mkdir -p /app/bin \
    && wget -q "https://msedgedriver.azureedge.net/${EDGE_VERSION}/edgedriver_linux64.zip" -O /tmp/edgedriver.zip \
    && unzip /tmp/edgedriver.zip -d /app/bin/ \
    && rm /tmp/edgedriver.zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && rm -rf /opt/microsoft/msedge-dev/MEIPreload 

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add bin directory to PATH
ENV PATH="/app/bin:${PATH}"

CMD ["python", "app.py"]