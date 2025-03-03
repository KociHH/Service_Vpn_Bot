FROM python:3.13-slim
LABEL authors="meow"

ENTRYPOINT ["top", "-b"]

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]