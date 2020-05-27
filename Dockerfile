FROM python:3
WORKDIR /app
ADD *.py /app/
ADD requirements.txt /app/
add .env /app/
RUN pip install -r /app/requirements.txt
CMD ["python", "/app/main.py"]
