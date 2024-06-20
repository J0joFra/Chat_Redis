import tkinter as tk
import redis
import threading
import time

# Connessione a Redis
try:
    r = redis.Redis(host='redis-17160.c328.europe-west3-1.gce.redns.redis-cloud.com',
                    port=17160, db=0, charset="utf-8", decode_responses=True,
                    password="n7ZV42GWVg6uyskJc08vBw97Um7lJetQ")
    r.ping()  # Controlla la connessione
except redis.ConnectionError as e:
    print(f"Errore di connessione a Redis: {e}")
    exit(1)

# Funzione per gestire il login
def login(username, password):
    if r.exists(username):
        user_data = r.hgetall(username)
        if user_data.get("password") == password:
            return user_data
        else:
            return None
    else:
        user_data = {"username": username, "password": password}
        r.hmset(username, user_data)
        return user_data

# Funzione per gestire l'interazione utente
def menu_interattivo():
    root = tk.Tk()
    root.title("Applicazione di messaggistica")

    # Funzione per gestire il login
    def login_gui():
        username = username_entry.get()
        password = password_entry.get()
        user_data = login(username, password)
        if user_data:
            print(f"Benvenuto, {username}!")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            main_window(username)
        else:
            print("Accesso negato.")

    # Finestra di login
    login_window = tk.Frame(root)
    login_window.pack(padx=20, pady=20)

    username_label = tk.Label(login_window, text="Username:")
    username_label.pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    login_button = tk.Button(login_window, text="Login", command=login_gui)
    login_button.pack(pady=10)

    root.mainloop()

# Funzione per gestire la rubrica
def rubrica(username):
    rubrica_key = f"{username}_rubrica"
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)
    contatti = r.lrange(rubrica_key, 0, -1)
    return contatti

# Funzione per aggiungere un contatto alla rubrica
def aggiungi_contatto(username, nuovo_contatto):
    rubrica_key = f"{username}_rubrica"
    r.rpush(rubrica_key, nuovo_contatto)

# Funzione per rimuovere un contatto dalla rubrica
def rimuovi_contatto(username, contatto_da_rimuovere):
    rubrica_key = f"{username}_rubrica"
    r.lrem(rubrica_key, 0, contatto_da_rimuovere)

# Funzione per inviare e leggere messaggi
def chat_messaggi(mittente, destinatario):
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"

    def aggiorna_chat(chat_box):
        messaggi = r.lrange(chat_key, 0, -1)
        for messaggio in messaggi:
            chat_box.insert(tk.END, f"{messaggio}\n")
        ultimo_messaggio = len(messaggi)
        while True:
            time.sleep(2)
            messaggi = r.lrange(chat_key, 0, -1)
            if len(messaggi) > ultimo_messaggio:
                nuovi_messaggi = messaggi[ultimo_messaggio:]
                for messaggio in nuovi_messaggi:
                    chat_box.insert(tk.END, f"{messaggio}\n")
                ultimo_messaggio = len(messaggi)

    def invia_messaggio(chat_box, messaggio_entry):
        messaggio = messaggio_entry.get()
        if messaggio:
            r.rpush(chat_key, f"{mittente}: {messaggio}")
            messaggio_entry.delete(0, tk.END)

    chat_box_frame = tk.Frame(main_win)
    chat_box_frame.pack(padx=10, pady=10)

    chat_box = tk.Text(chat_box_frame, height=20, width=50)
    chat_box.pack()

    messaggio_entry = tk.Entry(chat_box_frame, width=40)
    messaggio_entry.pack(side=tk.LEFT, padx=5, pady=5)
    messaggio_entry.bind("<Return>", lambda event: invia_messaggio(chat_box, messaggio_entry))

    invia_button = tk.Button(chat_box_frame, text="Invia", command=lambda: invia_messaggio(chat_box, messaggio_entry))
    invia_button.pack(side=tk.LEFT)

    threading.Thread(target=lambda: aggiorna_chat(chat_box), daemon=True).start()

# Funzione per creare la finestra principale
def main_window(username):
    global main_win
    main_win = tk.Toplevel()
    main_win.title(f"Applicazione di messaggistica - {username}")

    # Funzione per mostrare la rubrica
    def show_rubrica():
        contatti = rubrica(username)
        rubrica_text.delete('1.0', tk.END)
        rubrica_text.insert(tk.END, f"Rubrica di {username}:\n")
        for contatto in contatti:
            rubrica_text.insert(tk.END, f"{contatto}\n")

    # Funzione per aggiungere un contatto
    def add_contatto():
        nuovo_contatto = nuovo_contatto_entry.get()
        aggiungi_contatto(username, nuovo_contatto)
        nuovo_contatto_entry.delete(0, tk.END)
        show_rubrica()

    # Funzione per rimuovere un contatto
    def remove_contatto():
        contatto_da_rimuovere = rimuovi_contatto_entry.get()
        rimuovi_contatto(username, contatto_da_rimuovere)
        rimuovi_contatto_entry.delete(0, tk.END)
        show_rubrica()

    # Funzione per avviare la modalità do not disturb (interrompi ricezione messaggi)


    # Funzione per avviare la chat
    def start_chat():
        destinatario = destinatario_entry.get()
        if destinatario:
            chat_messaggi(username, destinatario)

    # Frame per la rubrica
    rubrica_frame = tk.Frame(main_win)
    rubrica_frame.pack(padx=10, pady=10)

    rubrica_label = tk.Label(rubrica_frame, text="Rubrica:")
    rubrica_label.pack()

    rubrica_text = tk.Text(rubrica_frame, height=10, width=30)
    rubrica_text.pack()

    show_rubrica()

    # Frame per aggiungere un contatto
    add_contatto_frame = tk.Frame(main_win)
    add_contatto_frame.pack(padx=10, pady=10)

    add_contatto_label = tk.Label(add_contatto_frame, text="Aggiungi contatto:")
    add_contatto_label.pack(side=tk.LEFT)

    nuovo_contatto_entry = tk.Entry(add_contatto_frame)
    nuovo_contatto_entry.pack(side=tk.LEFT)

    add_contatto_button = tk.Button(add_contatto_frame, text="Aggiungi", command=add_contatto)
    add_contatto_button.pack(side=tk.LEFT)

    # Frame per rimuovere un contatto
    remove_contatto_frame = tk.Frame(main_win)
    remove_contatto_frame.pack(padx=10, pady=10)

    remove_contatto_label = tk.Label(remove_contatto_frame, text="Rimuovi contatto:")
    remove_contatto_label.pack(side=tk.LEFT)

    rimuovi_contatto_entry = tk.Entry(remove_contatto_frame)
    rimuovi_contatto_entry.pack(side=tk.LEFT)

    remove_contatto_button = tk.Button(remove_contatto_frame, text="Rimuovi", command=remove_contatto)
    remove_contatto_button.pack(side=tk.LEFT)

    # Frame per avviare la chat
    chat_frame = tk.Frame(main_win)
    chat_frame.pack(padx=10, pady=10)

    destinatario_label = tk.Label(chat_frame, text="Destinatario:")
    destinatario_label.pack(side=tk.LEFT)

    destinatario_entry = tk.Entry(chat_frame)
    destinatario_entry.pack(side=tk.LEFT)

    start_chat_button = tk.Button(chat_frame, text="Avvia chat", command=start_chat)
    start_chat_button.pack(side=tk.LEFT)

    # Frame per la modalità do not disturb

# Avvio del programma
if __name__ == "__main__":
    menu_interattivo()
