FROM python:3.11-bookworm

WORKDIR /app

# System deps for building/wheels (lxml, curl_cffi, etc.) and git for versioning
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential gcc libffi-dev libxml2-dev libxslt1-dev git \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1
# Ensure our package is on sys.path without referencing undefined vars during build
ENV PYTHONPATH=/app/moodswing_trading

COPY moodswing_trading/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY moodswing_trading ./moodswing_trading
COPY --chmod=755 docker/entrypoint.sh ./docker/entrypoint.sh
# Normalize Windows CRLF to LF just in case the host checkout used CRLF
RUN sed -i 's/\r$//' ./docker/entrypoint.sh

ENTRYPOINT ["./docker/entrypoint.sh"]