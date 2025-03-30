FROM debian:bookworm-slim as edge_installer

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates && \
    wget -q -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-edge.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-edge.gpg] https://packages.microsoft.com/repos/edge/ stable main" > /etc/apt/sources.list.d/microsoft-edge.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends microsoft-edge-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim

WORKDIR /app

# Copy only the essential Edge files
COPY --from=edge_installer /opt/microsoft/msedge /opt/microsoft/msedge
COPY --from=edge_installer /usr/bin/microsoft-edge /usr/bin/
COPY --from=edge_installer /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m scraper && \
    chown -R scraper:scraper /app
USER scraper

EXPOSE 50051
CMD ["python", "app.py"]