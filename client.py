import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import socket
import sqlite3
import threading
import json

class ChatWindow:
    def __init__(self, master, username, recipient):
        self.master = master
        self.username = username
        self.recipient = recipient

        self.master.configure(bg="#F0F0F0")
        
        self.chat_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, bg="#FFFFFF", fg="#000000", font=("Arial", 12), state=tk.DISABLED)
        self.chat_text.pack(padx=10, pady=10, fill="both", expand=True)

        self.message_entry = tk.Entry(master, bg="#FFFFFF", fg="#000000", font=("Arial", 12))
        self.message_entry.pack(side="bottom", fill="x", padx=10, pady=5)

        self.send_button = tk.Button(master, text="Send", command=self.send_message, bg="#4CAF50", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.send_button.pack(side="bottom", fill="x", padx=10, pady=5)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        self.client_socket.send(self.username.encode('utf-8'))

        threading.Thread(target=self.receive_messages).start()

    def send_message(self):
        message = self.message_entry.get()
        message_data = json.dumps({'type': 'message', 'recipient': self.recipient, 'content': message})
        self.client_socket.send(message_data.encode('utf-8'))
        self.chat_text.configure(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"You: {message}\n")
        self.chat_text.configure(state=tk.DISABLED)
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                message_data = json.loads(message)
                if message_data['type'] == 'message':
                    sender = message_data['sender']
                    content = message_data['content']
                    self.chat_text.configure(state=tk.NORMAL)
                    self.chat_text.insert(tk.END, f"{sender}: {content}\n")
                    self.chat_text.configure(state=tk.DISABLED)
            except:
                self.client_socket.close()
                break

class ChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Chat App")
        master.configure(bg="#F0F0F0")

        self.login_frame = tk.Frame(master, bg="#F0F0F0", pady=20)
        self.login_frame.pack()

        self.username_label = tk.Label(self.login_frame, text="Username:", bg="#F0F0F0", font=("Arial", 12))
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:", bg="#F0F0F0", font=("Arial", 12))
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login, bg="#4CAF50", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = sqlite3.connect('chat_app.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if c.fetchone():
            print("Login successful")
            self.login_frame.pack_forget()  # Hide login frame
            self.setup_chat_window(username)  # Setup chat window
        else:
            print("User not found, creating account...")
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("Account created and logged in")
            self.login_frame.pack_forget()  # Hide login frame
            self.setup_chat_window(username)  # Setup chat window
        conn.close()

    def setup_chat_window(self, username):
        self.username = username
        self.chat_frame = tk.Frame(self.master, bg="#F0F0F0")
        self.chat_frame.pack(fill="both", expand=True)

        # Left panel for contacts
        self.contacts_frame = tk.Frame(self.chat_frame, width=200, bg="#D3D3D3", padx=10, pady=10)
        self.contacts_frame.pack(side="left", fill="y")

        self.add_contact_button = tk.Button(self.contacts_frame, text="Add Contact", command=self.add_contact, bg="#4CAF50", fg="#FFFFFF", font=("Arial", 12, "bold"))
        self.add_contact_button.pack(pady=10)

        self.contacts_label = tk.Label(self.contacts_frame, text="Contacts", bg="#D3D3D3", font=("Arial", 12, "bold"))
        self.contacts_label.pack(pady=5)

        self.contacts_list = tk.Listbox(self.contacts_frame, font=("Arial", 12))
        self.contacts_list.pack(fill="both", expand=True, pady=5)
        self.contacts_list.bind('<Double-1>', self.open_chat_window)

        # Right panel for chat (initially empty)
        self.chat_area_frame = tk.Frame(self.chat_frame, bg="#F0F0F0")
        self.chat_area_frame.pack(side="right", fill="both", expand=True)

    def add_contact(self):
        username = simpledialog.askstring("Add Contact", "Enter the username:")
        if username:
            # Check if the user exists in the database
            conn = sqlite3.connect('chat_app.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            if c.fetchone():
                # Add to contact list if not already present
                if not username in self.contacts_list.get(0, tk.END):
                    self.contacts_list.insert(tk.END, username)
                else:
                    messagebox.showinfo("Info", "Contact already added.")
            else:
                messagebox.showerror("Error", "User does not exist.")
            conn.close()

    def open_chat_window(self, event):
        selection = self.contacts_list.curselection()
        if selection:
            recipient = self.contacts_list.get(selection[0])
            chat_window = tk.Toplevel(self.master)
            chat_window.configure(bg="#F0F0F0")
            ChatWindow(chat_window, self.username, recipient)

def main():
    root = tk.Tk()
    root.geometry("800x600")  # Set initial size of the window
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
