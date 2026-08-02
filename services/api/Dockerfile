FROM python:3.12-slim

ARG RECYCLEROS_BUILD_DATE=unknown
ARG RECYCLEROS_RELEASE_SHA=unknown

LABEL org.opencontainers.image.title="RecyclerOS Platform API" \
    org.opencontainers.image.created="${RECYCLEROS_BUILD_DATE}" \
    org.opencontainers.image.revision="${RECYCLEROS_RELEASE_SHA}" \
    org.opencontainers.image.source="https://github.com/cmhall6117-jpg/recycleros-platform"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/services/api/src

RUN groupadd --system recycleros \
    && useradd --system --gid recycleros --home-dir /app --shell /usr/sbin/nologin recycleros

WORKDIR /app

COPY services/api/requirements.txt services/api/requirements-postgres.txt /tmp/requirements/
RUN python -m pip install --no-cache-dir \
        -r /tmp/requirements/requirements.txt \
        -r /tmp/requirements/requirements-postgres.txt

COPY services/api/src /app/services/api/src
COPY services/api/pilot_entrypoint.py /app/services/api/pilot_entrypoint.py
COPY services/api/production_entrypoint.py /app/services/api/production_entrypoint.py
COPY services/api/production_bootstrap.py /app/services/api/production_bootstrap.py
COPY tools/scripts/rc1_postgres_migrate.py /app/tools/scripts/rc1_postgres_migrate.py
COPY database/migrations/postgres /app/database/migrations/postgres

RUN chown -R recycleros:recycleros /app

USER recycleros

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=4 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.getenv('PORT', '8000')}/v1/health/ready\", timeout=3)"]

ENTRYPOINT ["python", "services/api/pilot_entrypoint.py"]
