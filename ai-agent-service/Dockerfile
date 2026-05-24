FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Optional: install kube-score and kube-linter for validation
RUN curl -sSL "https://github.com/zegl/kube-score/releases/download/v1.19.0/kube-score_1.19.0_linux_amd64" -o /usr/local/bin/kube-score \
    && chmod +x /usr/local/bin/kube-score || true

RUN curl -sSL "https://github.com/stackrox/kube-linter/releases/download/v0.7.1/kube-linter-linux.tar.gz" -o /tmp/kube-linter.tar.gz \
    && tar -xzf /tmp/kube-linter.tar.gz -C /tmp \
    && mv /tmp/kube-linter /usr/local/bin/kube-linter \
    && chmod +x /usr/local/bin/kube-linter \
    && rm -rf /tmp/kube-linter.tar.gz || true

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

RUN mkdir -p uploads generated

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
