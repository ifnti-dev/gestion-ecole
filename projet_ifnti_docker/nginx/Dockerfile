FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ifnti.conf /etc/nginx/conf.d/ifnti.conf

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]

