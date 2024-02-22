#!/bin/bash

# Variables
SYSTEM_D_ROOT_PATH="$(pwd)"

# Move to /home directory
cd

# Variables
DB_NAME="ifnti_db"
DB_USER="ifnti"
DB_PASSWORD="ifnti"
BASE_DIR="$(pwd)/projets"
SERVICE_NAME="ifnti.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
GIT_REPOSITORY="https://github.com/ifnti-dev/gestion-ecole.git"
PROJECT_FOLDER_NAME="gestion-ecole"
PROJECT_ENV_FOLDER=".ifnti_env"

# 🚀 Création du fichier ifnti.service
echo "================================================================"
echo "🚀 Création du fichier $SERVICE_NAME"
echo "================================================================"
touch $BASE_DIR/$SERVICE_NAME
echo "[Unit]" > $BASE_DIR/$SERVICE_NAME
echo "Description=Process de l'application web IFNTI" >> $BASE_DIR/$SERVICE_NAME
echo "After=network.target" >> $BASE_DIR/$SERVICE_NAME
echo "[Service]" >> $BASE_DIR/$SERVICE_NAME
echo "User=root" >> $BASE_DIR/$SERVICE_NAME
echo "Group=root" >> $BASE_DIR/$SERVICE_NAME
echo "WorkingDirectory=$BASE_DIR/$PROJECT_FOLDER_NAME/" >> $BASE_DIR/$SERVICE_NAME
echo "ExecStart=$BASE_DIR/$PROJECT_ENV_FOLDER/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 projet_ifnti.wsgi:application" >> $BASE_DIR/$SERVICE_NAME
echo "[Install]" >> $BASE_DIR/$SERVICE_NAME
echo "WantedBy=multi-user.target" >> $BASE_DIR/$SERVICE_NAME

if [ -e "$SERVICE_FILE" ]; then
    echo "================================================================"
    echo "⛔️ Arrêt de $SERVICE_NAME"
    echo "================================================================"
    sudo systemctl stop $SERVICE_NAME

    echo "================================================================"
    echo "⛔️ Désactivation de $SERVICE_NAME"
    echo "================================================================"
    sudo systemctl disable $SERVICE_NAME

    echo "================================================================"
    echo "🗑️ Suppression du fichier $SERVICE_NAME"
    echo "================================================================"
    sudo rm $SERVICE_NAME

    echo "================================================================"
    echo "♻️ Reload du démon"
    echo "================================================================"
    sudo systemctl daemon-reload
fi

# Create projects folders
mkdir -p $BASE_DIR
cd $BASE_DIR

# 🚀 Installation des dépendances
echo "================================================================"
echo "🔍 🌀 Installation des dépendances en cours..."
echo "================================================================"
sudo apt-get install git postgresql texmaker python3-virtualenv redis

# 🌐 Création de la base de données et de l'utilisateur
echo "================================================================"
echo "⚙️ Configuration de la base de données..."
echo "================================================================"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER password $DB_PASSWORD;"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 🌀 Création de l'environnement virtuel
echo "================================================================"
echo "🔧 Création de l'environnement virtuel..."
echo "================================================================"
virtualenv $PROJECT_ENV_FOLDER

# 🚀 Activation de l'environnement virtuel
echo "================================================================"
echo "🚀 Activation de l'environnement virtuel..."
echo "================================================================"
source $PROJECT_ENV_FOLDER/bin/activate

if [ ! -d "$PROJECT_FOLDER_NAME" ]; then
    git clone $GIT_REPOSITORY
fi

cd $PROJECT_FOLDER_NAME

cp $SYSTEM_D_ROOT_PATH/.env .env

# 📦 Installation des dépendances Python
echo "================================================================"
echo "📦 Installation des dépendances Python..."
echo "================================================================"
$BASE_DIR/$PROJECT_ENV_FOLDER/pip install -r requirements.txt

# ⚙️ Création des migrations
echo "================================================================"
echo "⚙️ Création des migrations..."
echo "================================================================"
$BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py makemigrations

# 🚚 Application des migrations
echo "================================================================"
echo "🚚 Application des migrations..."
echo "================================================================"
$BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py migrate

# 🚚 Application des migrations
echo "================================================================"
echo "🚚 Insertion des données de base..."
echo "================================================================"
$BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py factory

# 👤 Créer un superuser
echo "================================================================"
echo "👤 Création d'un superutilisateur..."
echo "================================================================"
$BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py createsuperuser

echo "================================================================"
echo "📄 Copie de $SERVICE_NAME vers : $SERVICE_FILE"
echo "================================================================"
sudo cp $BASE_DIR/$SERVICE_NAME $SERVICE_FILE

echo "================================================================"
echo "▶️ Démarrage de $SERVICE_NAME"
echo "================================================================"
sudo systemctl start $SERVICE_NAME

echo "================================================================"
echo "🔔 Activation de $SERVICE_NAME"
echo "================================================================"
sudo systemctl enable $SERVICE_NAME

echo "================================================================"
echo "♻️ Reload du démon"
echo "================================================================"
sudo systemctl daemon-reload
sudo systemctl status $SERVICE_NAME


echo "✅ Configuration terminée !"
