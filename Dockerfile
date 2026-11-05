FROM python:3.12-slim

# Без .pyc і з негайним виводом у консоль (видно в docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

COPY converter.py .

ENV AMOUNT=100 \
    FROM=USD \
    TO=EUR

CMD ["python", "converter.py"]
