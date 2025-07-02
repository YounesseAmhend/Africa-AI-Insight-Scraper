# Stage 1: Prepare environment, install build-only deps, generate gRPC stubs
FROM python:3.12-slim AS builder

WORKDIR /app

# 1) Install OS dependencies & Microsoft Edge + EdgeDriver
RUN apt-get update && apt-get install -y \
      wget gnupg apt-transport-https unzip --no-install-recommends \
    && wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" \
         > /etc/apt/sources.list.d/microsoft-edge-dev.list \
    && apt-get update \
    && apt-get install -y microsoft-edge-dev \
    && EDGE_VERSION=$(microsoft-edge --version | awk '{print $3}') \
    && mkdir -p /opt/msedgedriver \
    && wget -q "https://msedgedriver.azureedge.net/${EDGE_VERSION}/edgedriver_linux64.zip" \
         -O /tmp/edgedriver.zip \
    && unzip /tmp/edgedriver.zip -d /opt/msedgedriver/ \
    && chmod +x /opt/msedgedriver/msedgedriver \
    && rm /tmp/edgedriver.zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /opt/microsoft/msedge-dev/MEIPreload


# 4) Copy application code
COPY . .

# Stage 2: Slim runtime image
FROM python:3.12-slim AS runner
WORKDIR /app

# 1) Install runtime dependencies and Edge browser
RUN apt-get update && apt-get install -y \
      wget gnupg apt-transport-https unzip --no-install-recommends \
    && wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" \
         > /etc/apt/sources.list.d/microsoft-edge-dev.list \
    && apt-get update \
    && apt-get install -y microsoft-edge-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*
    
# 2) Install Python dependencies
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy application code and Edge driver
COPY --from=builder /app /app
COPY --from=builder /opt/msedgedriver /opt/msedgedriver

# 4) Set up Edge driver environment and permissions
ENV PATH="/opt/msedgedriver:${PATH}"
RUN chmod +x /opt/msedgedriver/msedgedriver \
    && ln -s /opt/msedgedriver/msedgedriver /usr/local/bin/msedgedriver

# 5) Expose gRPC port and start the server
EXPOSE 3013
CMD ["python", "app.py"]