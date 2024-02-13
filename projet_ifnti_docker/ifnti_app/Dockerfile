FROM python:3.10-alpine

COPY .gitenv /app/.gitenv

RUN apk update \
    && apk add python3-dev build-base linux-headers pcre-dev \
    && apk add git redis texmf-dist texlive \
    && source /app/.gitenv && git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/ifnti-dev/gestion-ecole.git \
    && mkdir -p app && mv gestion-ecole app/ifnti \
    && pip install --upgrade pip \
    && cd /app/ifnti && pip install -r requirements.txt

WORKDIR /app/ifnti

#RUN addgroup -r www-data && adduser -r -g www-data www-data 
#     && chown -R www-data:www-data /app/ifnti/staticfiles \
RUN chmod o+rx -R /app/ifnti/staticfiles

COPY settings.py projet_ifnti/settings.py
COPY .env .
COPY init_db.sh .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "--workers=1", "--bind", "unix:/app/gunicorn.sock", "projet_ifnti.wsgi:application"]

