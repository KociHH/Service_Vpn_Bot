FROM python:3.13-slim
LABEL authors="kosini"

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]