FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ifnti.conf /etc/nginx/conf.d/ifnti.conf

# RUN addgroup -r www-data && adduser -r -g www-data www-data \
#     && chown -R www-data:www-data /app/ifnti/staticfiles \
#     && chmod o+rx -R /app/ifnti/staticfiles


ENTRYPOINT [ "nginx", "-g", "daemon off;" ]

