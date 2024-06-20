import redis
import os

# Connessione a Redis
try:
    r = redis.Redis(host='redis-17160.c328.europe-west3-1.gce.redns.redis-cloud.com',
                    port=17160, db=0, charset="utf-8", decode_responses=True,
                    password="n7ZV42GWVg6uyskJc08vBw97Um7lJetQ")
    r.ping()  # Controlla la connessione
    print("Connessione a Redis riuscita!")
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
        if r.exists(username): # Username esistente
            user_data = r.hgetall(username)
            password = input(f"Username: {username}\nInserisci la password: ")
            if user_data.get("password") == password:
                return user_data
            else:
                clear_screen()
                print("Password errata.")
        else: # Username non esistente
            password = input("Crea una nuova password: ")
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hmset(username, user_data)
            return user_data

# Funzione per gestire l'interazione utente
def menu_interattivo():
    username = input("Inserisci il tuo username: ")
    user_data = login(username)
    if user_data:
        print(f"Benvenuto, {username}!")

        while True:
            clear_screen()
            print("=========================")
            print("Operazioni disponibili:")
            print("1. Mostra rubrica")
            print("2. Aggiungi contatto")
            print("3. Rimuovi contatto")
            print("4. Invia messaggio")
            print("5. Leggi messaggi")
            print("6. Modalità non disturbare")
            print("e. Esci")
            print("=========================")

            scelta = input("Inserisci il numero dell'operazione da eseguire o 'e' per uscire: ")

            if scelta == "1":
                clear_screen()
                contatti = rubrica(username)
                print(f"Rubrica di {username}:")
                for contatto in contatti:
                    print(contatto)
                input("\nPremi invio per tornare al menu...")
#=================================================================

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

    destinatario_data = r.hgetall(destinatario)

    def aggiorna_chat():
        ultimo_messaggio = 0
        while True:
            time.sleep(2)
            messaggi = r.lrange(chat_key, 0, -1)
            if len(messaggi) > ultimo_messaggio:
                nuovi_messaggi = messaggi[ultimo_messaggio:]
                for messaggio in nuovi_messaggi:
                    if messaggio.startswith(">"):
                        print(f"{messaggio}")
                    else:
                        print(f"< {messaggio}")
                ultimo_messaggio = len(messaggi)

    threading.Thread(target=aggiorna_chat, daemon=True).start()

    while True:
        messaggio = input(f"Inserisci un messaggio per {destinatario}: ")
        if messaggio.strip().lower() == 'exit':
            break
        messaggio = "> " + messaggio
        if destinatario_data.get("dnd") == "True":
            print(f"Errore! Messaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key, messaggio)

# Funzione per avviare la sessione
def avvia_sessione():
    while True:
        print("\nOpzioni disponibili:")
        print("1. Login")
        print("2. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        if scelta == '1':
            username = input("Username: ")
            password = input("Password: ")
            user_data = login(username, password)
            if user_data:
                print(f"Benvenuto, {username}!")
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
            elif scelta == "2":
                clear_screen()
                nuovo_contatto = input("Inserisci il nome del nuovo contatto da aggiungere: ")
                aggiungi_contatto(username, nuovo_contatto)
                print(f"Contatto '{nuovo_contatto}' aggiunto alla rubrica.")
                input("\nPremi invio per tornare al menu...")

            elif scelta == "3":
                clear_screen()
                contatto_da_rimuovere = input("Inserisci il nome del contatto da rimuovere: ")
                rimuovi_contatto(username, contatto_da_rimuovere)
                print(f"Contatto '{contatto_da_rimuovere}' rimosso dalla rubrica.")
                input("\nPremi invio per tornare al menu...")

            elif scelta == "4":
                clear_screen()
                destinatario = input("Inserisci il nome del destinatario del messaggio: ")
                destinatario_data = r.hgetall(destinatario)
                if destinatario_data.get("dnd") == "True":
                    print(f"Errore! Messaggio non recapitato perché il destinatario è in modalità non disturbare.")
                else:
                    messaggio = input("Inserisci il messaggio da inviare: ")
                    invia_messaggio(username, destinatario, messaggio)
                    print(f"Messaggio inviato a '{destinatario}'.")
                input("\nPremi invio per tornare al menu...")

            elif scelta == "5":
                clear_screen()
                destinatario = input("Inserisci il nome del mittente dei messaggi da leggere: ")
                messaggi = leggi_messaggi(username, destinatario)
                print(f"Messaggi tra te e '{destinatario}':")
                for messaggio in messaggi:
                    print(messaggio)
                input("\nPremi invio per tornare al menu...")

            elif scelta == "6":
                clear_screen()
                dnd_status = user_data.get("dnd") == "True"
                new_dnd_status = not dnd_status
                user_data["dnd"] = str(new_dnd_status)
                r.hmset(username, user_data)
                print(f"Modalità non disturbare {'attivata' if new_dnd_status else 'disattivata'}.")
                input("\nPremi invio per tornare al menu...")

            elif scelta == "e":
                print("Grazie per aver usato il servizio. Arrivederci!")
                break

            else:
                print("Scelta non valida. Riprova.")
                input("\nPremi invio per tornare al menu...")

    else:
        print("Accesso negato.")
        input("\nPremi invio per uscire...")

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

# Funzione per inviare un messaggio a un contatto
def invia_messaggio(mittente, destinatario, messaggio):
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    r.rpush(chat_key, f"{mittente}: {messaggio}")

# Funzione per leggere i messaggi da un contatto
def leggi_messaggi(username, destinatario):
    lista = [username, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    messaggi = r.lrange(chat_key, 0, -1)
    return messaggi

# Avvio del programma
if __name__ == "__main__":
    menu_interattivo()



