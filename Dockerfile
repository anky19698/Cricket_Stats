FROM python:3

WORKDIR /app

EXPOSE 8080

COPY . ./

RUN pip3 install -r requirements.txt

CMD streamit run --server.port 8080 --server.enableCORS false cricket_stats_app.py
