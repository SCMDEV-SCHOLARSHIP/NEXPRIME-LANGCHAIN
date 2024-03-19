FROM python:3.9-slim

WORKDIR /backend

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .
COPY gunicorn_conf.py /backend/gunicorn_conf.py

CMD ["gunicorn", "-c", "/backend/gunicorn_conf.py", "app:app"]