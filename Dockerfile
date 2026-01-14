FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
COPY start.sh .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
