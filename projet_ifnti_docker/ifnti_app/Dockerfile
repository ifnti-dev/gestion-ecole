FROM python:3.10-alpine

RUN apk update \
    && apk add python3-dev build-base linux-headers pcre-dev git \
    && apk add textlive \
    && apk install texlive-lang-french
    
RUN git clone https://github.com/ifnti-dev/ifnti-gestion.git \
    && mkdir app && mv ifnti-gestion app/ifnti
RUN pip install --upgrade pip
WORKDIR /app/ifnti
COPY settings.py projet_ifnti/settings.py
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT ["gunicorn", "--workers=1", "--bind", "unix:/app/ifnti/projet_ifnti/static/gunicorn.sock", "projet_ifnti.wsgi:application"]

