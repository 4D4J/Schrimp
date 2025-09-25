#!/bin/bash
# Schrimp Chat deployment script for Linux VPS

set -e

echo "Schrimp Chat - VPS deployment script"
echo "====================================="

# Default configuration
DEFAULT_PORT=8888
DEFAULT_USER="schrimp"
DEFAULT_DIR="/opt/schrimp-chat"

# Ask for configuration
read -p "Listening port [$DEFAULT_PORT]: " PORT
PORT=${PORT:-$DEFAULT_PORT}

read -p "System user [$DEFAULT_USER]: " USERNAME
USERNAME=${USERNAME:-$DEFAULT_USER}

read -p "Installation directory [$DEFAULT_DIR]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}

read -s -p "Chat password (optional): " PASSWORD
echo

# Check permissions
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (sudo)"
   exit 1
fi

echo "Installing dependencies..."
# Update system
apt update -y

# Install Python3 if necessary
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    apt install -y python3 python3-pip
fi

# Create system user if necessary
if ! id "$USERNAME" &>/dev/null; then
    echo "Creating user $USERNAME..."
    useradd -r -s /bin/false -d $INSTALL_DIR $USERNAME
fi

# Create installation directory
echo "Creating directory $INSTALL_DIR..."
mkdir -p $INSTALL_DIR
chown $USERNAME:$USERNAME $INSTALL_DIR

# Copy files
echo "Copying files..."
cp chat_server.py $INSTALL_DIR/
cp server.py $INSTALL_DIR/
cp logger.py $INSTALL_DIR/
cp client_manager.py $INSTALL_DIR/
cp auth_handler.py $INSTALL_DIR/
cp message_handler.py $INSTALL_DIR/
chown -R $USERNAME:$USERNAME $INSTALL_DIR/
chmod +x $INSTALL_DIR/chat_server.py

# Create logs directory
echo "Creating logs directory..."
mkdir -p $INSTALL_DIR/logs
chown $USERNAME:$USERNAME $INSTALL_DIR/logs

# Create systemd service
echo "Configuring systemd service..."
cat > /etc/systemd/system/schrimp-chat.service << EOF
[Unit]
Description=Schrimp Chat Server
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/chat_server.py $PORT${PASSWORD:+ "$PASSWORD"} $INSTALL_DIR/logs/schrimp_chat.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure firewall (UFW)
echo "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow $PORT/tcp
    echo "Port $PORT opened in UFW"
else
    echo "UFW not installed - configure your firewall manually"
fi

# Enable and start service
echo "Activating service..."
systemctl daemon-reload
systemctl enable schrimp-chat
systemctl start schrimp-chat

# Check status
sleep 2
if systemctl is-active --quiet schrimp-chat; then
    echo "Service started successfully!"
else
    echo "Error starting service"
    systemctl status schrimp-chat
    exit 1
fi

# Display final information
echo ""
echo "Installation completed!"
echo "======================"
echo "Server: $(hostname -I | awk '{print $1}'):$PORT"
echo "Connection: nc $(hostname -I | awk '{print $1}') $PORT"
if [[ -n "$PASSWORD" ]]; then
    echo "Password: $PASSWORD"
fi
echo ""
echo "Useful commands:"
echo "  Status:    systemctl status schrimp-chat"
echo "  Stop:      systemctl stop schrimp-chat"
echo "  Start:     systemctl start schrimp-chat"
echo "  Logs:      journalctl -u schrimp-chat -f"
echo "  Chat logs: tail -f $INSTALL_DIR/logs/schrimp_chat.log"
echo ""
echo "Files:"
echo "  Service:   /etc/systemd/system/schrimp-chat.service"
echo "  Code:      $INSTALL_DIR/"
echo "  Chat logs: $INSTALL_DIR/logs/schrimp_chat.log"