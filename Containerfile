FROM python:3.11-slim
WORKDIR /data
COPY . /data
RUN pip install --no-cache-dir requests beautifulsoup4 tqdm
ENTRYPOINT ["python", "app.py"]
CMD ["--help"]