import redis

# Connessione a Redis
r = redis.Redis(host='localhost', port=6380, db=0, charset="utf-8", decode_responses=True, password="miao")

# Funzione per gestire il login
def login(username):
    if r.exists(username):
        # L'utente esiste già, chiedi la password
        user_data = r.hgetall(username)
        password = input("Inserisci la password: ")
        if user_data.get("password") == password:
            return user_data
        else:
            print("Password errata.")
            return None
    else:
        # Nuovo utente, crea una nuova chiave e chiedi la password
        password = input("Crea una nuova password: ")
        user_data = {"username": username, "password": password}
        r.hmset(username, user_data)
        return user_data

# Funzione per gestire l'interazione utente
def menu_interattivo():
    username = input("Inserisci il tuo username: ")
    user_data = login(username)
    if user_data:
        print(f"Benvenuto, {username}!")

        while True:
            print("")
            print("=========================")
            print("Operazioni disponibili:")
            print("1. Mostra rubrica")
            print("2. Aggiungi contatto")
            print("3. Rimuovi contatto")
            print("4. Invia messaggio")
            print("5. Leggi messaggi")
            print("e. Esci")
            print("=========================")

            scelta = input("Inserisci il numero dell'operazione da eseguire o 'e' per uscire: ")

            if scelta == "1":
                contatti = rubrica(username)
                print(f"Rubrica di {username}:")
                for contatto in contatti:
                    print(contatto)

            elif scelta == "2":
                nuovo_contatto = input("Inserisci il nome del nuovo contatto da aggiungere: ")
                aggiungi_contatto(username, nuovo_contatto)
                print(f"Contatto '{nuovo_contatto}' aggiunto alla rubrica.")

            elif scelta == "3":
                contatto_da_rimuovere = input("Inserisci il nome del contatto da rimuovere: ")
                rimuovi_contatto(username, contatto_da_rimuovere)
                print(f"Contatto '{contatto_da_rimuovere}' rimosso dalla rubrica.")

            elif scelta == "4":
                destinatario = input("Inserisci il nome del destinatario del messaggio: ")
                messaggio = input("Inserisci il messaggio da inviare: ")
                invia_messaggio(username, destinatario, messaggio)
                print(f"Messaggio inviato a '{destinatario}'.")

            elif scelta == "5":
                destinatario = input("Inserisci il nome del mittente dei messaggi da leggere: ")
                messaggi = leggi_messaggi(username, destinatario)
                print(f"Messaggi tra te e '{destinatario}':")
                for messaggio in messaggi:
                    print(messaggio)

            elif scelta == "e":
                print("Grazie per aver usato il servizio. Arrivederci!")
                break

            else:
                try:
                    scelta_numerica = int(scelta)
                    print("Scelta non valida. Riprova.")
                except ValueError:
                    print("Scelta non valida. Riprova.")

    else:
        print("Accesso negato.")

# Funzione per gestire la rubrica
def rubrica(username):
    # Crea una chiave per la rubrica dell'utente
    rubrica_key = f"{username}_rubrica"

    # Se la rubrica non esiste, creala
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)

    # Restituisci la lista di contatti nella rubrica
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
    # Crea una chiave per la chat tra mittente e destinatario
    chat_key = f"{mittente}_{destinatario}"

    # Aggiungi il messaggio alla chat
    r.rpush(chat_key, f"{mittente}: {messaggio}")

# Funzione per leggere i messaggi da un contatto
def leggi_messaggi(username, destinatario):
    chat_key = f"{username}_{destinatario}"
    messaggi = r.lrange(chat_key, 0, -1)
    return messaggi

# Avvio del programma
if __name__ == "__main__":
    menu_interattivo()
