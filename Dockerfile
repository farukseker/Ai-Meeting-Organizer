FROM python:3.13-slim

WORKDIR /app


RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8051

CMD ["streamlit", "run", "main.py"]
