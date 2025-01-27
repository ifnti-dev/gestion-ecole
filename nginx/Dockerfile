# Utiliser l'image officielle de Nginx comme base
FROM nginx:latest

# Copier la configuration personnalisée dans le conteneur
COPY nginx.conf /etc/nginx/nginx.conf

COPY conf.d/app.conf /etc/nginx/conf.d/app.conf

# Exposer le port 80 pour le trafic HTTP
EXPOSE 80

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]