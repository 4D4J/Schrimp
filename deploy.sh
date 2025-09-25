#!/bin/bash
# Script de déploiement Schrimp Chat pour VPS Linux

set -e

echo "🦐 Schrimp Chat - Script de déploiement VPS"
echo "=========================================="

# Configuration par défaut
DEFAULT_PORT=8888
DEFAULT_USER="schrimp"
DEFAULT_DIR="/opt/schrimp-chat"

# Demander la configuration
read -p "Port d'écoute [$DEFAULT_PORT]: " PORT
PORT=${PORT:-$DEFAULT_PORT}

read -p "Utilisateur système [$DEFAULT_USER]: " USERNAME
USERNAME=${USERNAME:-$DEFAULT_USER}

read -p "Répertoire d'installation [$DEFAULT_DIR]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}

read -s -p "Mot de passe du chat (optionnel): " PASSWORD
echo

# Vérifier les permissions
if [[ $EUID -ne 0 ]]; then
   echo "❌ Ce script doit être exécuté en tant que root (sudo)"
   exit 1
fi

echo "📦 Installation des dépendances..."
# Mettre à jour le système
apt update -y

# Installer Python3 si nécessaire
if ! command -v python3 &> /dev/null; then
    echo "📥 Installation de Python3..."
    apt install -y python3 python3-pip
fi

# Créer l'utilisateur système si nécessaire
if ! id "$USERNAME" &>/dev/null; then
    echo "👤 Création de l'utilisateur $USERNAME..."
    useradd -r -s /bin/false -d $INSTALL_DIR $USERNAME
fi

# Créer le répertoire d'installation
echo "📁 Création du répertoire $INSTALL_DIR..."
mkdir -p $INSTALL_DIR
chown $USERNAME:$USERNAME $INSTALL_DIR

# Copier les fichiers
echo "📋 Copie des fichiers..."
cp chat_server.py $INSTALL_DIR/
chown $USERNAME:$USERNAME $INSTALL_DIR/chat_server.py
chmod +x $INSTALL_DIR/chat_server.py

# Créer le service systemd
echo "⚙️ Configuration du service systemd..."
cat > /etc/systemd/system/schrimp-chat.service << EOF
[Unit]
Description=Schrimp Chat Server
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/chat_server.py $PORT${PASSWORD:+ "$PASSWORD"}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configurer le firewall (UFW)
echo "🔥 Configuration du firewall..."
if command -v ufw &> /dev/null; then
    ufw allow $PORT/tcp
    echo "✅ Port $PORT ouvert dans UFW"
else
    echo "⚠️ UFW non installé - configurez manuellement votre firewall"
fi

# Activer et démarrer le service
echo "🚀 Activation du service..."
systemctl daemon-reload
systemctl enable schrimp-chat
systemctl start schrimp-chat

# Vérifier le statut
sleep 2
if systemctl is-active --quiet schrimp-chat; then
    echo "✅ Service démarré avec succès!"
else
    echo "❌ Erreur lors du démarrage du service"
    systemctl status schrimp-chat
    exit 1
fi

# Afficher les informations finales
echo ""
echo "🎉 Installation terminée!"
echo "========================"
echo "📡 Serveur: $(hostname -I | awk '{print $1}'):$PORT"
echo "🔗 Connexion: nc $(hostname -I | awk '{print $1}') $PORT"
if [[ -n "$PASSWORD" ]]; then
    echo "🔒 Mot de passe: $PASSWORD"
fi
echo ""
echo "📋 Commandes utiles:"
echo "  Statut:    systemctl status schrimp-chat"
echo "  Arrêter:   systemctl stop schrimp-chat"
echo "  Démarrer:  systemctl start schrimp-chat"
echo "  Logs:      journalctl -u schrimp-chat -f"
echo ""
echo "🔧 Fichiers:"
echo "  Service:   /etc/systemd/system/schrimp-chat.service"
echo "  Code:      $INSTALL_DIR/chat_server.py"