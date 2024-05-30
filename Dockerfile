FROM python:3

WORKDIR /app

COPY . ./

RUN pip3 install -r requirement.txt

CMD streamit run --server.port 8080 --server.enableCORS false cricket_stats_app.py
