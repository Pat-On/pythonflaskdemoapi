FROM python:3

WORKDIR /usr/src/app
COPY requirments.txt
RUN pip install --no-cache-dir - r requirements.txt
COPY . .
CMD ["python", "app.py"]