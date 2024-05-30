FROM python:3

WORKDIR /app

COPY . ./

RUN pip3 install -r requirement.txt

ENTRYPOINT ["streamlit", "run", "cricket_stats_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
