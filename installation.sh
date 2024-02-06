#!/bin/bash

# Variables

DB_NAME="ifnti_db"
DB_USER="ifnti"
DB_PASSWORD="ifnti"

# 🚀 Installation des dépendances
echo "🔍 🌀 Installation des dépendances en cours..."
sudo apt-get install postgresql texmaker python3-virtualenv redis

# 🌐 Création de la base de données et de l'utilisateur
echo "⚙️ Configuration de la base de données..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER;"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 🌀 Création de l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
virtualenv ../.ifnti_env

# 🚀 Activation de l'environnement virtuel
echo "🚀 Activation de l'environnement virtuel..."
source ../ifnti_env/bin/activate

# 📦 Installation des dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

# ⚙️ Création des migrations
echo "⚙️ Création des migrations..."
python3 manage.py makemigrations

# 🚚 Application des migrations
echo "🚚 Application des migrations..."
python3 manage.py migrate

echo "✅ Configuration terminée !"
