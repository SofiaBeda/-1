import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext

clients = {}
addresses = {}
conversations = {}  # To keep track of all messages

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Server Chat Monitor")

        self.convo_listbox = tk.Listbox(master)
        self.convo_listbox.pack(side="left", fill="both", expand=True)
        self.convo_listbox.bind("<<ListboxSelect>>", self.display_conversation)

        self.chat_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_text.pack(side="right", fill="both", expand=True)

    def display_conversation(self, event):
        selection = self.convo_listbox.curselection()
        if selection:
            selected_client = self.convo_listbox.get(selection[0])
            self.chat_text.configure(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            if selected_client in conversations:
                for message in conversations[selected_client]:
                    self.chat_text.insert(tk.END, f"{message}\n")
            self.chat_text.configure(state=tk.DISABLED)

    def update_conversation_list(self):
        self.convo_listbox.delete(0, tk.END)
        for client in clients:
            self.convo_listbox.insert(tk.END, client)

def handle_client(client_socket, client_address):
    username = client_socket.recv(1024).decode('utf-8')
    clients[username] = client_socket
    addresses[client_socket] = username
    conversations[username] = []

    gui.update_conversation_list()

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            message_data = json.loads(message)
            
            if message_data['type'] == 'message':
                recipient = message_data['recipient']
                msg = message_data['content']
                if recipient in clients:
                    response = json.dumps({'type': 'message', 'sender': username, 'content': msg})
                    clients[recipient].send(response.encode('utf-8'))
                    # Log the conversation
                    conversations[username].append(f"You to {recipient}: {msg}")
                    conversations[recipient].append(f"{username}: {msg}")
                    # Update GUI
                    gui.update_conversation_list()
            elif message_data['type'] == 'status':
                print(f"Status from {username}: {message_data['status']}")
        except:
            client_socket.close()
            del clients[username]
            del addresses[client_socket]
            del conversations[username]
            gui.update_conversation_list()
            break

def main():
    global gui
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen()

    root = tk.Tk()
    gui = ServerGUI(root)

    threading.Thread(target=accept_clients, args=(server_socket,), daemon=True).start()

    root.mainloop()

def accept_clients(server_socket):
    while True:
        client, address = server_socket.accept()
        print(f"Connection from {address} has been established.")
        client_handler = threading.Thread(target=handle_client, args=(client, address))
        client_handler.start()

if __name__ == "__main__":
    main()
