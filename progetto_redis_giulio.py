import redis
import threading
import time
import os

# Connessione a Redis
try:
    r = redis.Redis(host='redis-17160.c328.europe-west3-1.gce.redns.redis-cloud.com',
                    port=17160, db=0, charset="utf-8", decode_responses=True,
                    password="n7ZV42GWVg6uyskJc08vBw97Um7lJetQ")
    r.ping()  # Controlla la connessione
except redis.ConnectionError as e:
    print(f"Errore di connessione a Redis: {e}")
    exit(1)
# Pulizia schermo
def clear_screen():
    if os.name == 'nt':  # Se il sistema operativo è Windows
        os.system('cls')
    else:  # Altri sistemi operativi (Unix, Linux, Mac)
        os.system('clear')

# Funzione per gestire il login
def login(username):
    while True:
        if r.exists(username):  # Username esistente
            user_data = r.hgetall(username)
            password = input(f"Username: {username}\nInserisci la password: ")
            clear_screen()
            if user_data.get("password") == password:
                return user_data
            else:
                clear_screen()
                print("Password errata.")
        else:  # Username non esistente
            password = input("Crea una nuova password: ")
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hmset(username, user_data)
            return user_data

# Funzione per gestire la rubrica
def rubrica(username):
    clear_screen()
    rubrica_key = f"{username}_rubrica"
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)
    contatti = r.lrange(rubrica_key, 0, -1)
    return contatti

# Funzione per aggiungere un contatto alla rubrica
def aggiungi_contatto(username, nuovo_contatto):
    clear_screen()
    rubrica_key = f"{username}_rubrica"
    r.rpush(rubrica_key, nuovo_contatto)

# Funzione per rimuovere un contatto dalla rubrica
def rimuovi_contatto(username, contatto_da_rimuovere):
    clear_screen()
    rubrica_key = f"{username}_rubrica"
    r.lrem(rubrica_key, 0, contatto_da_rimuovere)

# Funzione per inviare e leggere messaggi
def chat_messaggi(mittente, destinatario):
    clear_screen()
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"

    destinatario_data = r.hgetall(destinatario)

    def aggiorna_chat():
        ultimo_messaggio = 0
        while True:
            time.sleep(2)
            messaggi = r.lrange(chat_key, 0, -1)
            if len(messaggi) > ultimo_messaggio:
                nuovi_messaggi = messaggi[ultimo_messaggio:]
                for messaggio in nuovi_messaggi:
                    if messaggio.startswith("Me >> "):
                        print(f"{messaggio}")
                    else:
                        print(f"{destinatario} << {messaggio}")
                ultimo_messaggio = len(messaggi)
                time.sleep(3) #3 sec

    threading.Thread(target=aggiorna_chat, daemon=True).start()

    while True:
        messaggio = input() # Solo input del messaggio, senza prompt
        if messaggio.strip().lower() == 'exit':
            break
        messaggio = "Me >> " + messaggio  # Formatta il messaggio
        if destinatario_data.get("dnd") == "True":
            print(f"Errore! Messaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key, messaggio)
        clear_screen()  # Cancella l'input e mostra solo i messaggi

# Funzione per avviare la sessione
def avvia_sessione():
    while True:
        clear_screen()
        print("Opzioni disponibili:")
        print("1. Login")
        print("2. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        if scelta == '1':
            username = input("Username: ")
            password = input("Password: ")
            user_data = login(username, password)
            if user_data:
                loading = 0
                print(f"Benvenuto, {username}!")
                time.sleep(5)
                while loading < 100:
                    clear_screen()
                    print(f"Loading: {loading}%")
                    loading += 20
                    time.sleep(0.5)
                    
                while True:
                    print("\nOpzioni disponibili:")
                    print("1. Mostra rubrica")
                    print("2. Aggiungi contatto")
                    print("3. Rimuovi contatto")
                    print("4. Avvia chat")
                    print("5. Logout")
                    opzione = input("Inserisci il numero dell'opzione desiderata: ")

                    if opzione == '1':
                        contatti = rubrica(username)
                        print(f"Rubrica di {username}:")
                        for contatto in contatti:
                            print(contatto)

                    elif opzione == '2':
                        nuovo_contatto = input("Inserisci il nuovo contatto: ")
                        aggiungi_contatto(username, nuovo_contatto)
                        print(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")

                    elif opzione == '3':
                        contatto_da_rimuovere = input("Inserisci il contatto da rimuovere: ")
                        rimuovi_contatto(username, contatto_da_rimuovere)
                        print(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

                    elif opzione == '4':
                        destinatario = input("Inserisci il destinatario della chat: ")
                        chat_messaggi(username, destinatario)

                    elif opzione == '5':
                        print(f"Logout effettuato per l'utente {username}.")
                        break

                    else:
                        print("Opzione non valida. Riprova.")

            else:
                print("Accesso negato. Username o password errati.")

        elif scelta == '2':
            print("Grazie per aver usato l'applicazione.")
            break

        else:
            print("Opzione non valida. Riprova.")

# Avvio del programma
if __name__ == "__main__":
    avvia_sessione()
