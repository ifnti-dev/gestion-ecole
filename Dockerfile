FROM python:3.10-alpine

WORKDIR /app
COPY . .

# install uwsgi setup
RUN apk add python3-dev build-base linux-headers pcre-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#ENTRYPOINT ["/bin/sleep","3600000"]
#CMD [ "uwsgi", "--ini", "/app/projet_ifnti.uwsgi.ini" ]

RUN chmod +x ./docker-entrypoint.sh