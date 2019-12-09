FROM python:3.6.8-alpine3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apk add git \
    && python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8080"]