FROM python:3.12-slim

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
COPY tools/scripts/rc1_postgres_migrate.py /app/tools/scripts/rc1_postgres_migrate.py
COPY database/migrations/postgres /app/database/migrations/postgres

RUN chown -R recycleros:recycleros /app

USER recycleros

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=4 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/v1/health/ready', timeout=3)"]

ENTRYPOINT ["python", "services/api/pilot_entrypoint.py"]
