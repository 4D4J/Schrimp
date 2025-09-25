#!/usr/bin/env python3
"""
Script de test pour le serveur de chat Schrimp
Simule plusieurs clients pour tester le serveur
"""

import socket
import threading
import time
import sys

class TestClient:
    def __init__(self, host, port, pseudo, password=None):
        self.host = host
        self.port = port
        self.pseudo = pseudo
        self.password = password
        self.socket = None
        self.running = False
        
    def connect(self):
        """Se connecte au serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            # Recevoir le message de bienvenue
            welcome = self.socket.recv(1024).decode('utf-8')
            print(f"[{self.pseudo}] Reçu: {welcome}")
            
            # Authentification si nécessaire
            if self.password and "mot de passe" in welcome.lower():
                self.socket.send(f"{self.password}\n".encode('utf-8'))
                auth_response = self.socket.recv(1024).decode('utf-8')
                print(f"[{self.pseudo}] Auth: {auth_response}")
            
            # Envoyer le pseudo
            self.socket.send(f"{self.pseudo}\n".encode('utf-8'))
            
            # Démarrer le thread de réception
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"[{self.pseudo}] Erreur de connexion: {e}")
            return False
    
    def receive_messages(self):
        """Reçoit les messages du serveur"""
        while self.running:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    print(f"[{self.pseudo}] << {message.strip()}")
                else:
                    break
            except:
                break
    
    def send_message(self, message):
        """Envoie un message"""
        if self.running and self.socket:
            try:
                self.socket.send(f"{message}\n".encode('utf-8'))
                print(f"[{self.pseudo}] >> {message}")
            except Exception as e:
                print(f"[{self.pseudo}] Erreur envoi: {e}")
    
    def disconnect(self):
        """Se déconnecte"""
        self.running = False
        if self.socket:
            try:
                self.socket.send("/quit\n".encode('utf-8'))
                self.socket.close()
            except:
                pass
        print(f"[{self.pseudo}] Déconnecté")

def test_multiple_clients():
    """Test avec plusieurs clients simulés"""
    host = 'localhost'
    port = 8888
    password = None
    
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    
    print(f"🧪 Test du serveur {host}:{port}")
    if password:
        print(f"🔒 Mot de passe: {password}")
    
    # Créer plusieurs clients de test
    clients = [
        TestClient(host, port, "Alice", password),
        TestClient(host, port, "Bob", password),
        TestClient(host, port, "Charlie", password)
    ]
    
    # Connecter tous les clients
    connected_clients = []
    for client in clients:
        if client.connect():
            connected_clients.append(client)
            time.sleep(0.5)  # Petit délai entre les connexions
    
    if not connected_clients:
        print("❌ Aucun client n'a pu se connecter")
        return
    
    print(f"✅ {len(connected_clients)} clients connectés")
    
    # Simulation de conversation
    time.sleep(2)
    
    # Alice envoie un message
    if len(connected_clients) > 0:
        connected_clients[0].send_message("Salut tout le monde!")
    
    time.sleep(1)
    
    # Bob répond
    if len(connected_clients) > 1:
        connected_clients[1].send_message("Salut Alice! Comment ça va?")
    
    time.sleep(1)
    
    # Charlie utilise une commande
    if len(connected_clients) > 2:
        connected_clients[2].send_message("/users")
    
    time.sleep(1)
    
    # Alice répond à Bob
    if len(connected_clients) > 0:
        connected_clients[0].send_message("Ça va bien Bob, merci!")
    
    time.sleep(2)
    
    # Déconnexion progressive
    print("\n🔌 Déconnexion des clients...")
    for i, client in enumerate(connected_clients):
        client.disconnect()
        time.sleep(0.5)
    
    print("✅ Test terminé")

def interactive_client():
    """Client interactif pour tester manuellement"""
    host = input("IP du serveur (localhost): ").strip() or 'localhost'
    port = int(input("Port (8888): ").strip() or '8888')
    password = input("Mot de passe (vide si aucun): ").strip() or None
    pseudo = input("Votre pseudo: ").strip() or f"TestUser_{port}"
    
    client = TestClient(host, port, pseudo, password)
    
    if client.connect():
        print("✅ Connecté! Tapez vos messages (ou 'quit' pour quitter)")
        try:
            while client.running:
                message = input()
                if message.lower() in ['quit', 'exit', '/quit']:
                    break
                client.send_message(message)
        except KeyboardInterrupt:
            pass
        finally:
            client.disconnect()
    else:
        print("❌ Impossible de se connecter")

if __name__ == "__main__":
    print("🧪 Testeur Schrimp Chat")
    print("1. Test automatique avec plusieurs clients")
    print("2. Client interactif")
    
    choice = input("Votre choix (1/2): ").strip()
    
    if choice == "1":
        test_multiple_clients()
    elif choice == "2":
        interactive_client()
    else:
        print("Choix invalide, lancement du test automatique...")
        test_multiple_clients()