FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY server.py .
COPY tools/ tools/
COPY utils/ utils/

RUN pip install --no-cache-dir -e .

EXPOSE 8006

CMD ["python", "server.py"]
