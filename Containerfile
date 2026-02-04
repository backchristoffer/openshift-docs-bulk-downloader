FROM python:3.11-slim
RUN pip install --no-cache-dir requests beautifulsoup4 tqdm
WORKDIR /app
COPY app.py .
WORKDIR /data
ENTRYPOINT ["python", "/app/app.py"]
CMD ["--help"]