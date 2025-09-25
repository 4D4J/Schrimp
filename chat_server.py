#!/usr/bin/env python3
"""
Serveur de Chat Simple - Schrimp
Permet aux utilisateurs de se connecter via netcat (nc) pour chatter
Usage: python chat_server.py [port] [password]
Connexion client: nc <ip_serveur> <port>
"""

import socket
import threading
import time
import sys
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='0.0.0.0', port=8888, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.clients = {}  # {socket: {'pseudo': str, 'ip': str, 'connected_at': datetime}}
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Démarre le serveur de chat"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"🚀 Serveur de chat démarré sur {self.host}:{self.port}")
            if self.password:
                print(f"🔒 Mot de passe requis: {self.password}")
            else:
                print("🔓 Aucun mot de passe requis")
            print(f"📡 Connexion: nc {self.host} {self.port}")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"📞 Nouvelle connexion de {client_address[0]}:{client_address[1]}")
                    
                    # Créer un thread pour chaque client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("❌ Erreur lors de l'acceptation de connexion")
                        
        except Exception as e:
            print(f"❌ Erreur de démarrage du serveur: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Gère un client connecté"""
        pseudo = None
        authenticated = False
        
        try:
            # Message de bienvenue
            welcome_msg = "\n" + "="*50 + "\n"
            welcome_msg += "🦐 Bienvenue sur Schrimp Chat!\n"
            welcome_msg += "="*50 + "\n"
            
            if self.password:
                welcome_msg += "🔒 Mot de passe requis\n"
                welcome_msg += "Entrez le mot de passe: "
            else:
                welcome_msg += "Entrez votre pseudo: "
                authenticated = True
                
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Authentification si nécessaire
            if self.password:
                password_attempt = client_socket.recv(1024).decode('utf-8').strip()
                if password_attempt == self.password:
                    authenticated = True
                    client_socket.send("✅ Authentification réussie!\nEntrez votre pseudo: ".encode('utf-8'))
                else:
                    client_socket.send("❌ Mot de passe incorrect. Connexion fermée.\n".encode('utf-8'))
                    return
            
            if authenticated:
                # Demander le pseudo
                pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
                pseudo = pseudo_input if pseudo_input else f"Anonyme_{client_address[1]}"
                
                # Vérifier si le pseudo est déjà pris
                while any(client_info['pseudo'] == pseudo for client_info in self.clients.values()):
                    client_socket.send(f"❌ Pseudo '{pseudo}' déjà pris. Choisissez-en un autre: ".encode('utf-8'))
                    pseudo_input = client_socket.recv(1024).decode('utf-8').strip()
                    pseudo = pseudo_input if pseudo_input else f"Anonyme_{client_address[1]}"
                
                # Enregistrer le client
                self.clients[client_socket] = {
                    'pseudo': pseudo,
                    'ip': client_address[0],
                    'connected_at': datetime.now()
                }
                
                # Messages de connexion
                join_msg = f"✅ {pseudo} a rejoint le chat!"
                print(f"👤 {pseudo} ({client_address[0]}) connecté")
                self.broadcast_message(join_msg, exclude_client=client_socket)
                
                # Envoyer les infos de connexion au client
                info_msg = f"\n🎉 Connecté en tant que: {pseudo}\n"
                info_msg += f"👥 Utilisateurs connectés: {len(self.clients)}\n"
                info_msg += "💡 Tapez vos messages et appuyez sur Entrée\n"
                info_msg += "💡 Tapez '/quit' pour quitter\n"
                info_msg += "💡 Tapez '/users' pour voir les utilisateurs connectés\n"
                info_msg += "-" * 30 + "\n"
                client_socket.send(info_msg.encode('utf-8'))
                
                # Boucle de réception des messages
                while self.running:
                    try:
                        message = client_socket.recv(1024).decode('utf-8').strip()
                        if not message:
                            break
                            
                        # Commandes spéciales
                        if message.lower() == '/quit':
                            break
                        elif message.lower() == '/users':
                            users_list = "👥 Utilisateurs connectés:\n"
                            for client_info in self.clients.values():
                                users_list += f"  • {client_info['pseudo']} ({client_info['ip']})\n"
                            client_socket.send(users_list.encode('utf-8'))
                            continue
                        
                        # Diffuser le message
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        formatted_message = f"[{timestamp}] {pseudo}: {message}"
                        print(formatted_message)
                        self.broadcast_message(formatted_message, exclude_client=client_socket)
                        
                    except socket.error:
                        break
                        
        except Exception as e:
            print(f"❌ Erreur avec le client {client_address}: {e}")
        finally:
            # Nettoyage lors de la déconnexion
            if client_socket in self.clients:
                pseudo = self.clients[client_socket]['pseudo']
                del self.clients[client_socket]
                
                disconnect_msg = f"👋 {pseudo} a quitté le chat"
                print(f"👤 {pseudo} déconnecté")
                self.broadcast_message(disconnect_msg)
                
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast_message(self, message, exclude_client=None):
        """Diffuse un message à tous les clients connectés"""
        disconnected_clients = []
        
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude_client:
                try:
                    client_socket.send((message + "\n").encode('utf-8'))
                except socket.error:
                    disconnected_clients.append(client_socket)
        
        # Nettoyer les clients déconnectés
        for client_socket in disconnected_clients:
            if client_socket in self.clients:
                pseudo = self.clients[client_socket]['pseudo']
                del self.clients[client_socket]
                print(f"👤 {pseudo} déconnecté (erreur réseau)")
    
    def stop(self):
        """Arrête le serveur"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("\n🛑 Serveur arrêté")

def main():
    # Gestion des arguments de ligne de commande
    port = 8888
    password = None
    
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Port invalide, utilisation du port par défaut 8888")
    
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    
    # Créer et démarrer le serveur
    server = ChatServer(port=port, password=password)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        server.stop()

if __name__ == "__main__":
    main()