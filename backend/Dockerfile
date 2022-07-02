FROM python:3.7-slim

WORKDIR /app

COPY /backend .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]
