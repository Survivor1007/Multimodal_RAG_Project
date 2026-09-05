# ==========================================
# Stage 1: Build Stage (Compile dependencies into virtualenv)
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install temporary build toolchain
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Minimal Runtime Stage (~60% smaller image)
# ==========================================
FROM python:3.10-slim AS runner

WORKDIR /app

# Copy pre-compiled virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY . /app/

# Create required directories for FAISS indexes & telemetry logs
RUN mkdir -p /app/data/indexes /app/logs /app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
