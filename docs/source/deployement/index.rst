Documentation pour deploy.sh
============================

Introduction
------------

Cette documentation explique ligne par ligne le script ``deploy.sh``, qui automatise le déploiement de l'application web IFNTI.

Aperçu du Script
----------------

Le script ``deploy.sh`` gère le déploiement de l'application IFNTI en effectuant les tâches suivantes :

1. **Configuration du Service :** Configure et gère un service systemd (``ifnti.service``) pour exécuter l'application web.

2. **Configuration de la Base de Données :** Configure une base de données PostgreSQL et un utilisateur pour l'application.

3. **Configuration de l'Environnement :** Crée un environnement virtuel Python et installe les dépendances du projet.

4. **Initialisation du Projet :** Clone le dépôt du projet, copie la configuration de l'environnement et effectue les migrations Django.

5. **Gestion du Service systemd :** Gère le cycle de vie du service systemd - arrêt, désactivation et suppression du service s'il existe déjà.

Directives du Script
--------------------

1. **Variables :**

    .. code-block:: bash

        SYSTEM_D_ROOT_PATH="$(pwd)"

    Définit le chemin racine pour le service systemd.

    Déplacement vers le répertoire /home :

    .. code-block:: bash

        cd

    Déplace vers le répertoire personnel.

    Variables de Configuration du Service et de la Base de Données :

    .. code-block:: bash

        DB_NAME="ifnti_db"
        DB_USER="ifnti"
        DB_PASSWORD="ifnti"
        BASE_DIR="$(pwd)/projets"
        SERVICE_NAME="ifnti.service"
        SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
        GIT_REPOSITORY="https://github.com/ifnti-dev/gestion-ecole.git"
        PROJECT_FOLDER_NAME="gestion-ecole"
        PROJECT_ENV_FOLDER=".ifnti_env"

    Définit des variables pour la configuration de la base de données, du projet et du service.

    Création du Fichier de Service systemd :

    .. code-block:: bash

        echo "🚀 Création du fichier $SERVICE_NAME"
        touch $BASE_DIR/$SERVICE_NAME
        # ... (création du contenu)

    Crée le fichier de service systemd s'il n'existe pas, avec des configurations spécifiques.

    Gestion du Service Existante :

    .. code-block:: bash

        if [ -e "$SERVICE_FILE" ]; then
            # ... (arrêt, désactivation, suppression et rechargement du démon systemd)
        fi

    Vérifie si le fichier de service existe et gère le service existant en conséquence.

    Création des Répertoires du Projet :

    .. code-block:: bash

        mkdir -p $BASE_DIR
        cd $BASE_DIR

    Crée la structure des répertoires du projet.

    Installation des Dépendances :

    .. code-block:: bash

        echo "🔍 🌀 Installation des dépendances en cours..."
        sudo apt-get install git postgresql texmaker python3-virtualenv redis

    Installe les dépendances nécessaires à l'aide de apt-get.

    Configuration de la Base de Données PostgreSQL :

    .. code-block:: bash

        echo "⚙️ Configuration de la base de données..."
        # ... (configuration de la base de données PostgreSQL et de l'utilisateur)

    Configure la base de données PostgreSQL et l'utilisateur pour l'application.

    Création et Activation de l'Environnement Virtuel :

    .. code-block:: bash

        echo "🔧 Création de l'environnement virtuel..."
        # ... (création et activation de l'environnement virtuel Python)

    Crée et active l'environnement virtuel Python.

    Clone du Dépôt du Projet :

    .. code-block:: bash

        if [ ! -d "$PROJECT_FOLDER_NAME" ]; then
            git clone $GIT_REPOSITORY
        fi
        cd $PROJECT_FOLDER_NAME
        cp $SYSTEM_D_ROOT_PATH/.env .env

    Clone le dépôt du projet s'il n'existe pas et copie la configuration de l'environnement.

    Installation des Dépendances Python :

    .. code-block:: bash

        echo "📦 Installation des dépendances Python..."
        $BASE_DIR/$PROJECT_ENV_FOLDER/pip install -r requirements.txt

    Installe les dépendances Python à l'aide de pip.

    Migrations Django :

    .. code-block:: bash

        echo "⚙️ Création des migrations..."
        $BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py makemigrations
        echo "🚚 Application des migrations..."
        $BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py migrate

    Effectue les migrations de base de données Django.

    Insertion des Données de Base :

    .. code-block:: bash

        echo "🚚 Insertion des données de base..."
        $BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py factory

    Insère des données de base dans la base de données.

    Création du Superutilisateur :

    .. code-block:: bash

        echo "👤 Création d'un superutilisateur..."
        $BASE_DIR/$PROJECT_ENV_FOLDER/bin/python3 manage.py createsuperuser

    Crée un superutilisateur pour l'application Django.

    Copie du Fichier de Service et Activation du Service :

    .. code-block:: bash

        echo "📄 Copie de $SERVICE_NAME vers : $SERVICE_FILE"
        sudo cp $BASE_DIR/$SERVICE_NAME $SERVICE_FILE
        echo "▶️ Démarrage de $SERVICE_NAME"
        sudo systemctl start $SERVICE_NAME
        echo "🔔 Activation de $SERVICE_NAME"
        sudo systemctl enable $SERVICE_NAME

    Copie le fichier de service systemd dans le répertoire approprié et démarre/active le service.

    Rechargement du Démon et Vérification de l'État :

    .. code-block:: bash

        echo "♻️ Reload du démon"
        sudo systemctl daemon-reload
        sudo systemctl status $SERVICE_NAME

    Recharge le démon systemd et vérifie l'état du service.

2. Message de Conclusion :

    .. code-block:: bash

        echo "✅ Configuration terminée !"

Conclusion
----------

Ce script automatise le processus de déploiement et de configuration de l'application web IFNTI, couvrant la configuration du service, la configuration de la base de données, la création de l'environnement, l'initialisation du projet et la gestion du service systemd.
