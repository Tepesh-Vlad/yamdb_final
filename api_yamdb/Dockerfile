FROM python:3.7-slim
WORKDIR /app
RUN echo ls
COPY api_yamdb/requirements.txt .
RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY api_yamdb/ .

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]
LABEL author='Tepesh-Vlad' version=2

