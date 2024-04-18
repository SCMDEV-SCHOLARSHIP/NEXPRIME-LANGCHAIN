FROM python:3.11-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./backend /backend

WORKDIR /

RUN mkdir /nsa_files

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--app-dir", "/backend"]