FROM python:3.10.17-slim

ENV PYTHONPATH=/workspace

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini ./

RUN mkdir -p logs

CMD ["python", "-m", "app"]