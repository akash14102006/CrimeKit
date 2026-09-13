# ============================================================
# CrimeKit Backend - Production Multi-Stage Dockerfile
# ============================================================

# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /build

# System deps for building native extensions (neo4j driver, Pillow, bcrypt,
# pytsk3, libewf-python). python3-dev provides Python.h for C extensions.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        make \
        python3-dev \
        libffi-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libtsk-dev \
        libewf-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps with pip cache mounted for faster rebuilds
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install --no-warn-script-location \
        -r requirements.txt

# Build libewf-python from source (pip install fails due to configure
# dependency-tracking issue; manual build with --disable-dependency-tracking works)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip download --no-binary :all: libewf-python==20240506 -d /tmp/ewf_src && \
    cd /tmp/ewf_src && \
    tar xzf libewf-python-20240506.tar.gz && \
    cd libewf-20240506 && \
    sh configure --prefix=/install --disable-nls --disable-shared-libs --disable-dependency-tracking && \
    make -j$(nproc) && \
    make install && \
    python3 -m pip install --no-deps --prefix=/install . && \
    cd / && rm -rf /tmp/ewf_src

# Copy application source
COPY . .

# ---- Stage 2: Runtime ----
FROM python:3.12-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# OCI image labels
LABEL org.opencontainers.image.source="https://github.com/user/crimekit" \
      org.opencontainers.image.description="CrimeKit Backend API" \
      org.opencontainers.image.title="CrimeKit Backend" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="MIT"

# Runtime system deps (only shared libs, no compilers)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libtsk19t64 \
        libewf2 \
        tesseract-ocr \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 1000 crimekit && \
    useradd --uid 1000 --gid crimekit --create-home crimekit

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=crimekit:crimekit --from=builder /build /app

# Ensure required storage and log directories exist with correct user ownership
RUN mkdir -p /app/backend/storage/evidence /app/storage/evidence /app/logs && \
    chown -R crimekit:crimekit /app

WORKDIR /app

# Ensure logs aren't buffered
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8002

EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')"]

USER crimekit

ENTRYPOINT ["python"]
CMD ["-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
