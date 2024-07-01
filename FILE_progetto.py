# Importa i moduli necessari
import redis
import threading
import time
import os
from datetime import datetime
from colorama import Fore, Style, init

# Inizializza il modulo colorama per utilizzare i colori nella console
init(autoreset=True)

# Connessione a Redis
try:
    # Crea un'istanza del client Redis con le credenziali fornite
    r = redis.Redis(host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
                    port=11602, db=0, charset="utf-8", decode_responses=True,
                    password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU")
    # Verifica la connessione a Redis
    r.ping()
except redis.ConnectionError as e:
    # Gestisce l'errore di connessione a Redis
    print(f"Errore di connessione a Redis: {e}")
    exit(1)

def clear_screen():
    # Verifica il sistema operativo
    if os.name == 'nt':
        # Esegue il comando 'cls' per Windows
        os.system('cls')
    else:
        # Esegue il comando 'clear' per Unix/Linux
        os.system('clear')

def login(username):
    while True:
        # Verifica se l'utente esiste nel database Redis
        if r.exists(username):
            # Recupera i dati dell'utente dal database
            user_data = r.hgetall(username)
            clear_screen()
            # Richiede la password all'utente
            password = input(f"Username: {username}\nInserisci la password: ")
            # Verifica se la password inserita è corretta
            if user_data.get("password") == password:
                # Restituisce i dati dell'utente se la password è corretta
                return user_data
            else:
                clear_screen()
                print("Password errata.")
        else:
            # Se l'utente non esiste, richiede la creazione di una nuova password
            password = input("Crea una nuova password: ")
            # Crea un nuovo utente nel database con i dati forniti
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hset(username, mapping=user_data)
            # Restituisce i dati dell'utente appena creato
            return user_data

# Funzione per ottenere la rubrica di un utente
def rubrica(username):
    # Costruisce la chiave per la rubrica dell'utente
    rubrica_key = f"{username}_rubrica"
    # Se la rubrica non esiste, la crea con l'username come primo contatto
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)
    # Recupera la lista dei contatti dalla rubrica
    contatti = r.lrange(rubrica_key, 0, -1)
    return contatti

def aggiungi_contatto(username, nuovo_contatto):
    clear_screen()
    # Costruisce la chiave per la rubrica dell'utente
    rubrica_key = f"{username}_rubrica"
    # Aggiunge il nuovo contatto alla rubrica
    r.rpush(rubrica_key, nuovo_contatto)

def rimuovi_contatto(username, contatto_da_rimuovere):
    clear_screen()
    # Costruisce la chiave per la rubrica dell'utente
    rubrica_key = f"{username}_rubrica"
    # Rimuove il contatto dalla rubrica
    r.lrem(rubrica_key, 0, contatto_da_rimuovere)

def chat_messaggi(mittente, destinatario):
    # Ordina gli username in ordine alfabetico per creare una chiave univoca per la chat
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    # Recupera i dati dell'utente destinatario
    destinatario_data = r.hgetall(destinatario)
    
    # Funzione per aggiornare la chat in tempo reale
    def aggiorna_chat():
        last_shown_index = 0
        try:
            while True:
                # Recupera tutti i messaggi della chat
                messaggi = r.lrange(chat_key, 0, -1)
                # Ottiene i nuovi messaggi non ancora visualizzati
                new_messages = messaggi[last_shown_index:]
                if new_messages:
                    for messaggio in new_messages:
                        # Estrae il timestamp dal messaggio
                        timestamp = messaggio[-5:]
                        # Formatta e stampa i messaggi inviati dal mittente
                        if messaggio.startswith(f"{mittente}: "):
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-5]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            # Formatta e stampa i messaggi inviati dal destinatario
                            if messaggio.startswith("\u00b7 "):
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-5]}\n{timestamp}")
                    # Aggiorna l'indice dell'ultimo messaggio visualizzato
                    last_shown_index += len(new_messages)
                time.sleep(1)
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")
    
    # Avvia un thread separato per l'aggiornamento della chat
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    
    while True:
        # Richiede all'utente di inserire un messaggio
        messaggio = input()
        if messaggio.strip().lower() == 'exit':
            # Esce dalla chat se l'utente digita 'exit'
            break
        # Formatta il messaggio con il timestamp
        timestamp = datetime.now().strftime('%H:%M')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        # Verifica se il destinatario è in modalità 'non disturbare'
        if destinatario_data.get("dnd") == "True":
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            # Aggiunge il messaggio alla chat
            r.rpush(chat_key, messaggio_formattato)

# Funzione per avviare una chat temporanea tra due utenti
def chat_messaggi_temporanea(mittente, destinatario):
    # Ordina gli username in ordine alfabetico per creare una chiave univoca per la chat
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}_temp"
    # Recupera i dati dell'utente destinatario
    destinatario_data = r.hgetall(destinatario)
    chat_attiva = True

    # Funzione per aggiornare la chat in tempo reale
    def aggiorna_chat():
        clear_screen()
        last_shown_index = 0
        try:
            while chat_attiva:
                # Recupera tutti i messaggi della chat
                messaggi = r.lrange(chat_key, 0, -1)
                # Ottiene i nuovi messaggi non ancora visualizzati
                new_messages = messaggi[last_shown_index:]
                if new_messages:
                    for messaggio in new_messages:
                        # Estrae il timestamp dal messaggio
                        timestamp = messaggio[-8:]
                        # Formatta e stampa i messaggi inviati dal mittente
                        if messaggio.startswith(f"{mittente}: "):
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-8]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            # Formatta e stampa i messaggi inviati dal destinatario
                            if messaggio.startswith("\u00b7 "):
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-8]}\n{timestamp}")
                    # Aggiorna l'indice dell'ultimo messaggio visualizzato
                    last_shown_index += len(new_messages)
                time.sleep(1)
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")

    # Funzione per monitorare il timeout della chat
    def monitor_chat_timeout():
        timeout_seconds = 0
        try:
            while chat_attiva:
                start_time = time.time()
                while chat_attiva:
                    time.sleep(1)
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= 60:
                        timeout_seconds += elapsed_time
                        break
                    if r.llen(chat_key) > 0:
                        timeout_seconds = 0
                
                if timeout_seconds >= 60:
                    # Elimina la chat se non ci sono messaggi per 60 secondi
                    r.delete(chat_key)
                    clear_screen()
                    print(f"\nLa chat tra {mittente} e {destinatario} è stata eliminata per inattività.")
                    time.sleep(5)
                    print("Premi INVIO per continuare...")
                    return True
        except Exception as e:
            print(f"Errore durante il monitoraggio della chat: {e}")
            return False
    
    # Avvia un thread separato per l'aggiornamento della chat
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    # Avvia un thread separato per il monitoraggio del timeout della chat
    monitor_thread = threading.Thread(target=monitor_chat_timeout)
    monitor_thread.start()

    while True:
        if not monitor_thread.is_alive():
            # Esce dalla chat se il thread di monitoraggio del timeout è terminato
            break

        # Richiede all'utente di inserire un messaggio
        messaggio = input()
        if messaggio.strip().lower() == 'exit':
            # Esce dalla chat se l'utente digita 'exit'
            break
        # Formatta il messaggio con il timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        # Verifica se il destinatario è in modalità 'non disturbare'
        if destinatario_data.get("dnd") == "True":
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            # Aggiunge il messaggio alla chat
            r.rpush(chat_key, messaggio_formattato)      

    # Termina la chat e rimuove la chiave dalla chat temporanea
    chat_attiva = False
    r.delete(chat_key)
    print(f"\nLa chat tra {mittente} e {destinatario} è stata chiusa.")
    time.sleep(2)

def toggle_dnd(username):
    # Recupera i dati dell'utente
    user_data = r.hgetall(username)
    # Ottiene lo stato attuale della modalità 'non disturbare'
    dnd_status = user_data.get("dnd", "False")
    # Inverte lo stato della modalità 'non disturbare'
    new_dnd_status = "False" if dnd_status == "True" else "True"
    # Aggiorna lo stato della modalità 'non disturbare' per l'utente
    r.hset(username, "dnd", new_dnd_status)
    clear_screen()
    if new_dnd_status == 'True':
        print("Modalità 'non disturbare' attivata")
    else:
        print("Modalità 'non disturbare' disattivata")
    time.sleep(2)

def cerca_utenti(parziale):
    clear_screen()
    # Ottiene tutte le chiavi nel database Redis
    chiavi = r.keys()
    risultati = []
    for chiave in chiavi:
        # Verifica se la chiave contiene la stringa parziale e non contiene il carattere ':'
        if parziale in chiave and ':' not in chiave:
            # Verifica se la chiave è di tipo 'hash' (rappresenta un utente)
            if r.type(chiave) == 'hash':
                risultati.append(chiave)
    
    if risultati:
        print("Risultati della ricerca:")
        for utente in risultati:
            print(utente)
    else:
        print("Nessun utente trovato.")
    input("\nPremi INVIO per continuare...")

def avvia_sessione():
    while True:
        clear_screen()
        print("Opzioni disponibili:")
        print("1. Login")
        print("2. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        if scelta == '1':
            # Richiede il nome utente per il login
            username = input("Username: ")
            # Effettua il login o la registrazione dell'utente
            user_data = login(username)
            if user_data:
                loading = 0
                print(f"Benvenuto, {username}!")
                width = 50
                for i in range(101):
                    # Visualizza una barra di caricamento
                    progress = "=" * int(width * i / 100)
                    spaces = " " * (width - len(progress))
                    print(f"\rLoading: [{progress}{spaces}] {i}%", end="", flush=True)
                    time.sleep(0.02)
                print("\nLoading complete!")
               
                while True:
                    clear_screen()              
                    print("Opzioni disponibili:")
                    print("1. Mostra rubrica")
                    print("2. Aggiungi contatto")
                    print("3. Rimuovi contatto")
                    print("4. Avvia chat")
                    print("5. Avvia chat a tempo")
                    print("6. Attiva/Disattiva modalità 'non disturbare'")
                    print("7. Cerca utenti")
                    print("8. Logout")
                    opzione = input("Inserisci il numero dell'opzione desiderata: ")

                    if opzione == '1':
                        # Pulisci lo schermo
                        clear_screen()
                        # Ottieni la rubrica dell'utente
                        contatti = rubrica(username)
                        # Stampa la rubrica dell'utente
                        print(f"Rubrica di {username}:")
                        for contatto in contatti:
                            print(contatto)
                        # Attendi l'input dell'utente per continuare
                        input("\nPremi INVIO per continuare...")

                    elif opzione == '2':
                        # Chiedi all'utente di inserire un nuovo contatto
                        nuovo_contatto = input("Inserisci un nuovo contatto: ")
                        # Verifica se il contatto esiste nel sistema
                        if r.exists(nuovo_contatto):
                            # Verifica se il contatto è già presente nella rubrica dell'utente
                            if nuovo_contatto not in rubrica(username):
                                # Aggiungi il nuovo contatto alla rubrica dell'utente
                                aggiungi_contatto(username, nuovo_contatto)
                                print(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")
                            else:
                                # Stampa un messaggio di errore se il contatto è già presente nella rubrica
                                print(f"Errore!\nIl contatto {nuovo_contatto} è già presente nella rubrica.")
                                time.sleep(3)
                        else:
                            # Stampa un messaggio di errore se il contatto non esiste nel sistema
                            print(f"Errore!\nIl contatto {nuovo_contatto} non è presente nel sistema.")
                            time.sleep(3)

                    elif opzione == '3':
                        # Chiedi all'utente di inserire il contatto da rimuovere
                        contatto_da_rimuovere = input("Inserisci il contatto da rimuovere: ")
                        # Rimuovi il contatto dalla rubrica dell'utente
                        rimuovi_contatto(username, contatto_da_rimuovere)
                        print(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

                    elif opzione == '4':
                        # Chiedi all'utente di inserire il destinatario della chat
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica dell'utente
                        if destinatario in rubrica(username):
                            # Avvia la chat con il destinatario
                            chat_messaggi(username, destinatario)
                        else:
                            # Stampa un messaggio di errore se il destinatario non è presente nella rubrica
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    elif opzione == '5':
                        # Chiedi all'utente di inserire il destinatario della chat temporanea
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica dell'utente
                        if destinatario in rubrica(username):
                            # Avvia la chat temporanea con il destinatario
                            chat_messaggi_temporanea(username, destinatario)
                        else:
                            # Stampa un messaggio di errore se il destinatario non è presente nella rubrica
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    elif opzione == '6':
                        # Attiva/Disattiva la modalità 'non disturbare' per l'utente
                        toggle_dnd(username)

                    elif opzione == '7':
                        # Chiedi all'utente di inserire il nome utente (anche parziale) da cercare
                        parziale = input("Inserisci il nome utente (anche parziale): ")
                        # Cerca gli utenti che corrispondono al nome utente parziale
                        cerca_utenti(parziale)

                    elif opzione == '8':
                        # Stampa un messaggio di logout per l'utente
                        print(f"Logout effettuato per l'utente {username}.")
                        break

                    else:
                        # Stampa un messaggio di errore se l'opzione inserita non è valida
                        print("Opzione non valida. Riprova.")

        elif scelta == '2':
            # Stampa un messaggio di uscita dall'applicazione
            print("Grazie per aver usato l'applicazione.")
            break
        else:
            # Stampa un messaggio di errore se l'opzione inserita non è valida
            print("Opzione non valida. Riprova.")

if __name__ == "__main__":
    # Avvia la sessione dell'applicazione
    avvia_sessione()

