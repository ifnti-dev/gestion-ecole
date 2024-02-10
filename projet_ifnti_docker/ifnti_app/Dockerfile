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

COPY settings.py projet_ifnti/settings.py
COPY .env .env
COPY init_db.sh .

EXPOSE 8000

ENTRYPOINT ["gunicorn", "--workers=1", "--bind", "unix:/app/ifnti/projet_ifnti/static/gunicorn.sock", "projet_ifnti.wsgi:application"]

