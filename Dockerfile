FROM python:3.9-alpine

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=True
ENV TZ=America/Los_Angeles

COPY requirements.txt /app/
RUN apk add --no-cache mariadb-dev mariadb-connector-c-dev build-base libffi-dev openssl-dev pkgconfig
RUN pip install -r requirements.txt
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
