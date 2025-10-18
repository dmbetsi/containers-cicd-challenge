FROM python:3.10-slim
WORKDIR /web_app

COPY app /web_app

RUN pip install --no-cache-dir -r app/requirements.txt

COPY .env /app



ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=${DATABASE_URL}
ENV SECRET_KEY=${SECRET_KEY}


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
