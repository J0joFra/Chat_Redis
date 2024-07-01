# Importa i moduli necessari
import redis # Modulo per interagire con il database Redis
import threading # Modulo per gestire i thread
import time # Modulo per gestire il tempo
import os # Modulo per interagire con il sistema operativo
from datetime import datetime # Modulo per gestire le date e le ore
from colorama import Fore, Style, init # Modulo per aggiungere colori alla console

# Inizializza il modulo colorama per utilizzare i colori nella console
init(autoreset=True)

# Connessione a Redis
try:
    # Crea un'istanza del client Redis con le credenziali fornite
    r = redis.Redis(host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
                    port=11602, db=0, charset="utf-8", decode_responses=True,
                    password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU") # Crea un'istanza del client Redis con le credenziali fornite
    # Verifica la connessione a Redis
    r.ping() # Verifica la connessione a Redis
except redis.ConnectionError as e:
    # Gestisce l'errore di connessione a Redis
    print(f"Errore di connessione a Redis: {e}") # Stampa un messaggio di errore se la connessione a Redis fallisce
    exit(1) # Esce dal programma

# Funzione per pulire la console
def clear_screen():
    if os.name == 'nt': # Se il sistema operativo è Windows
        os.system('cls') # Esegue il comando 'cls' per pulire la console
    else:
        os.system('clear') # Altrimenti, esegue il comando 'clear' per pulire la console

# Funzione per effettuare il login o la registrazione di un utente
def login(username):
    while True:
        if r.exists(f"user:{username}"): # Controlla se l'utente esiste nel database
            user_data = r.hgetall(f"user:{username}") # Ottiene i dati dell'utente dal database
            clear_screen()
            password = input(f"Username: {username}\nInserisci la password: ") # Chiede all'utente di inserire la password
            if user_data.get("password") == password: # Controlla se la password inserita è corretta
                return user_data # Restituisce i dati dell'utente se la password è corretta
            else:
                clear_screen()
                print("Password errata.") # Stampa un messaggio di errore se la password è sbagliata
        else:
            password = input("Crea una nuova password: ") # Chiede all'utente di creare una nuova password
            user_data = {"username": username, "password": password, "dnd": "False"} # Crea un dizionario con i dati dell'utente
            r.hset(f"user:{username}", mapping=user_data) # Salva i dati dell'utente nel database
            return user_data # Restituisce i dati dell'utente

# Funzione per ottenere la rubrica di un utente
def rubrica(username):
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    if not r.exists(rubrica_key): # Controlla se la rubrica esiste nel database
        r.rpush(rubrica_key, username) # Se non esiste, crea una nuova rubrica con l'username dell'utente
    contatti = r.lrange(rubrica_key, 0, -1) # Ottiene la lista dei contatti dalla rubrica
    return contatti # Restituisce la lista dei contatti

# Funzione per aggiungere un nuovo contatto alla rubrica di un utente
def aggiungi_contatto(username, nuovo_contatto):
    clear_screen()
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    r.rpush(rubrica_key, nuovo_contatto) # Aggiunge il nuovo contatto alla rubrica

# Funzione per rimuovere un contatto dalla rubrica di un utente
def rimuovi_contatto(username, contatto_da_rimuovere):
    clear_screen()
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    r.lrem(rubrica_key, 0, contatto_da_rimuovere) # Rimuove il contatto dalla rubrica

def chat_messaggi(mittente, destinatario):
    lista = sorted([mittente, destinatario]) # Ordina gli username in ordine alfabetico
    chat_key1 = f"chat:{lista[0]}:{lista[1]}" # Crea la chiave per la chat tra i due utenti
    chat_key2 = f"chat:{lista[1]}:{lista[0]}" # Crea la chiave per la chat tra i due utenti (invertita)
    destinatario_data = r.hgetall(f"user:{destinatario}") # Ottiene i dati dell'utente destinatario

    def crea_cartelle_chat():
        if not r.exists(chat_key1): # Controlla se la chat esiste nel database
            r.rpush(chat_key1, "") # Se non esiste, crea una nuova chat vuota
        if not r.exists(chat_key2): # Controlla se la chat esiste nel database
            r.rpush(chat_key2, "") # Se non esiste, crea una nuova chat vuota

    crea_cartelle_chat() # Crea le cartelle per la chat, se non esistono

    def aggiorna_chat():
        last_shown_index = 0 # Indice dell'ultimo messaggio mostrato
        try:
            while True:
                messaggi = r.lrange(chat_key1, 0, -1) # Ottiene la lista dei messaggi dalla chat
                new_messages = messaggi[last_shown_index:] # Ottiene i nuovi messaggi dalla lista
                if new_messages:
                    for messaggio in new_messages:
                        timestamp = messaggio[-5:] # Ottiene l'orario del messaggio
                        if messaggio.startswith(f"{mittente}: "): # Se il messaggio è stato inviato dal mittente
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-5] # Formatta il messaggio
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}") # Stampa il messaggio con il colore giallo
                        else:
                            if messaggio.startswith("\u00b7 "): # Se il messaggio è una risposta
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}") # Stampa il messaggio con il colore giallo
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-5]}\n{timestamp}") # Stampa il messaggio con il colore verde
                    last_shown_index += len(new_messages) # Aggiorna l'indice dell'ultimo messaggio mostrato
                time.sleep(1) # Aspetta un secondo prima di controllare nuovamente i nuovi messaggi
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}") # Stampa un messaggio di errore se si verifica un'eccezione

    threading.Thread(target=aggiorna_chat, daemon=True).start() # Avvia un nuovo thread per aggiornare la chat

    while True:
        messaggio = input() # Chiede all'utente di inserire un messaggio
        if messaggio.strip().lower() == 'exit': # Se l'utente inserisce 'exit', esce dal ciclo
            break
        timestamp = datetime.now().strftime('%H:%M') # Ottiene l'orario attuale
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}" # Formatta il messaggio con l'username e l'orario
        if destinatario_data.get("dnd") == "True": # Controlla se il destinatario è in modalità 'non disturbare'
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.") # Stampa un messaggio di errore
        else:
            r.rpush(chat_key1, messaggio_formattato) # Aggiunge il messaggio alla chat
            r.rpush(chat_key2, messaggio_formattato) # Aggiunge il messaggio alla chat (invertita)

# Funzione per avviare una chat temporanea tra due utenti
def chat_messaggi_temporanea(mittente, destinatario):
    # Ordina gli username in ordine alfabetico
    lista = sorted([mittente, destinatario])
    # Crea la chiave per la chat tra i due utenti
    chat_key1 = f"chat_temp:{lista[0]}:{lista[1]}"
    # Crea la chiave per la chat tra i due utenti (invertita)
    chat_key2 = f"chat_temp:{lista[1]}:{lista[0]}"
    # Ottiene i dati dell'utente destinatario
    destinatario_data = r.hgetall(f"user:{destinatario}")
    # Imposta la chat come attiva
    chat_attiva = True

    # Funzione per creare le cartelle per la chat, se non esistono
    def crea_cartelle_chat():
        # Controlla se la chat esiste nel database
        if not r.exists(chat_key1):
            # Se non esiste, crea una nuova chat vuota
            r.rpush(chat_key1, "")
        # Controlla se la chat esiste nel database
        if not r.exists(chat_key2):
            # Se non esiste, crea una nuova chat vuota
            r.rpush(chat_key2, "")

    # Chiama la funzione per creare le cartelle per la chat
    crea_cartelle_chat()

    # Funzione per aggiornare la chat
    def aggiorna_chat():
        # Pulisce lo schermo
        clear_screen()
        # Imposta l'indice dell'ultimo messaggio mostrato a 0
        last_shown_index = 0
        try:
            # Ciclo che continua finché la chat è attiva
            while chat_attiva:
                # Ottiene la lista dei messaggi dalla chat
                messaggi = r.lrange(chat_key1, 0, -1)
                # Ottiene i nuovi messaggi dalla lista
                new_messages = messaggi[last_shown_index:]
                # Se ci sono nuovi messaggi
                if new_messages:
                    # Ciclo per ogni nuovo messaggio
                    for messaggio in new_messages:
                        # Ottiene l'orario del messaggio
                        timestamp = messaggio[-8:]
                        # Se il messaggio è stato inviato dal mittente
                        if messaggio.startswith(f"{mittente}: "):
                            # Formatta il messaggio
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-8]
                            # Stampa il messaggio con il colore giallo
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            # Se il messaggio è una risposta
                            if messaggio.startswith("\u00b7 "):
                                # Stampa il messaggio con il colore giallo
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                # Stampa il messaggio con il colore verde
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-8]}\n{timestamp}")
                    # Aggiorna l'indice dell'ultimo messaggio mostrato
                    last_shown_index += len(new_messages)
                # Aspetta un secondo prima di controllare nuovamente i nuovi messaggi
                time.sleep(1)
        except Exception as e:
            # Stampa un messaggio di errore se si verifica un'eccezione
            print(f"Errore durante l'aggiornamento della chat: {e}")

    # Funzione per monitorare il timeout della chat
    def monitor_chat_timeout():
        # Inizializza il contatore del timeout a 0
        timeout_seconds = 0
        try:
            # Ciclo che continua finché la chat è attiva
            while chat_attiva:
                # Ottiene il tempo di inizio
                start_time = time.time()
                # Ciclo interno che continua finché la chat è attiva
                while chat_attiva:
                    # Aspetta un secondo
                    time.sleep(1)
                    # Calcola il tempo trascorso
                    elapsed_time = time.time() - start_time
                    # Se è trascorso un minuto
                    if elapsed_time >= 60:
                        # Aggiorna il contatore del timeout
                        timeout_seconds += elapsed_time
                        # Esce dal ciclo interno
                        break
                    # Se ci sono nuovi messaggi nella chat
                    if r.llen(chat_key1) > 0:
                        # Resetta il contatore del timeout
                        timeout_seconds = 0

                # Se il timeout è scaduto
                if timeout_seconds >= 60:
                    # Elimina le chiavi della chat dal database
                    r.delete(chat_key1)
                    r.delete(chat_key2)
                    # Pulisce lo schermo
                    clear_screen()
                    # Stampa un messaggio di notifica
                    print(f"\nLa chat tra {mittente} e {destinatario} è stata eliminata per inattività.")
                    # Aspetta 5 secondi
                    time.sleep(5)
                    # Chiede all'utente di premere INVIO per continuare
                    print("Premi INVIO per continuare...")
                    # Restituisce True per indicare che la chat è stata eliminata
                    return True
        except Exception as e:
            # Stampa un messaggio di errore se si verifica un'eccezione
            print(f"Errore durante il monitoraggio della chat: {e}")
            # Restituisce False per indicare che si è verificato un errore
            return False

    # Avvia un nuovo thread per aggiornare la chat
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    # Avvia un nuovo thread per monitorare il timeout della chat
    monitor_thread = threading.Thread(target=monitor_chat_timeout)
    monitor_thread.start()

    # Ciclo principale per inviare messaggi
    while True:
        # Se il thread di monitoraggio del timeout è terminato
        if not monitor_thread.is_alive():
            # Esce dal ciclo
            break

        # Chiede all'utente di inserire un messaggio
        messaggio = input()
        # Se l'utente inserisce 'exit'
        if messaggio.strip().lower() == 'exit':
            # Esce dal ciclo
            break
        # Ottiene l'orario attuale
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Formatta il messaggio con l'username e l'orario
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        # Controlla se il destinatario è in modalità 'non disturbare'
        if destinatario_data.get("dnd") == "True":
            # Stampa un messaggio di errore
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            # Aggiunge il messaggio alla chat
            r.rpush(chat_key1, messaggio_formattato)
            # Aggiunge il messaggio alla chat (invertita)
            r.rpush(chat_key2, messaggio_formattato)

    # Imposta la chat come non attiva
    chat_attiva = False
    # Elimina le chiavi della chat dal database
    r.delete(chat_key1)
    r.delete(chat_key2)
    # Stampa un messaggio di notifica
    print(f"\nLa chat tra {mittente} e {destinatario} è stata chiusa.")
    # Aspetta 2 secondi
    time.sleep(2)


# Funzione per attivare/disattivare la modalità 'non disturbare' per un utente
def toggle_dnd(username):
    # Ottiene i dati dell'utente
    user_data = r.hgetall(f"user:{username}")
    # Ottiene lo stato attuale della modalità 'non disturbare'
    dnd_status = user_data.get("dnd", "False")
    # Imposta il nuovo stato della modalità 'non disturbare'
    new_dnd_status = "False" if dnd_status == "True" else "True"
    # Aggiorna lo stato della modalità 'non disturbare' nel database
    r.hset(f"user:{username}", "dnd", new_dnd_status)
    # Pulisce lo schermo
    clear_screen()
    # Stampa un messaggio di notifica
    if new_dnd_status == 'True':
        print("Modalità 'non disturbare' attivata")
    else:
        print("Modalità 'non disturbare' disattivata")
    # Aspetta 2 secondi
    time.sleep(2)

# Funzione per cercare utenti nel database
def cerca_utenti(parziale):
    # Pulisce lo schermo
    clear_screen()
    # Ottiene tutte le chiavi che iniziano con "user:"
    chiavi = r.keys("user:*")
    # Inizializza una lista vuota per i risultati
    risultati = []
    # Ciclo per ogni chiave
    for chiave in chiavi:
        # Se la chiave contiene la stringa parziale
        if parziale in chiave:
            # Aggiunge l'username alla lista dei risultati
            risultati.append(chiave.split(":")[1])
    
    # Se ci sono risultati
    if risultati:
        # Stampa un messaggio di intestazione
        print("Risultati della ricerca:")
        # Ciclo per ogni risultato
        for utente in risultati:
            # Stampa l'username
            print(utente)
    else:
        # Stampa un messaggio di notifica
        print("Nessun utente trovato.")
    # Chiede all'utente di premere INVIO per continuare
    input("\nPremi INVIO per continuare...")

# Funzione principale per avviare la sessione dell'applicazione
def avvia_sessione():
    # Ciclo infinito per mantenere l'applicazione in esecuzione
    while True:
        # Pulisce lo schermo
        clear_screen()
        # Stampa le opzioni disponibili per l'utente
        print("Opzioni disponibili:")
        print("1. Login")
        print("2. Esci")
        # Chiede all'utente di inserire il numero dell'opzione desiderata
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        # Se l'utente sceglie l'opzione 1 (Login)
        if scelta == '1':
            # Chiede all'utente di inserire il proprio username
            username = input("Username: ")
            # Esegue la funzione di login con l'username inserito
            user_data = login(username)
            # Se il login ha avuto successo (user_data non è vuoto)
            if user_data:
                # Inizializza una variabile di caricamento a 0
                loading = 0
                # Stampa un messaggio di benvenuto
                print(f"Benvenuto, {username}!")
                # Imposta la larghezza della barra di caricamento
                width = 50
                # Ciclo per simulare una barra di caricamento
                for i in range(101):
                    # Calcola la lunghezza della barra di caricamento
                    progress = "=" * int(width * i / 100)
                    # Calcola gli spazi vuoti rimanenti
                    spaces = " " * (width - len(progress))
                    # Stampa la barra di caricamento con la percentuale di completamento
                    print(f"\rLoading: [{progress}{spaces}] {i}%", end="", flush=True)
                    # Aspetta 0.02 secondi prima di aggiornare la barra di caricamento
                    time.sleep(0.02)
                # Stampa un messaggio di completamento del caricamento
                print("\nLoading complete!")
               
                # Ciclo infinito per mantenere il menu dell'utente in esecuzione
                while True:
                    # Pulisce lo schermo
                    clear_screen()              
                    # Stampa le opzioni disponibili per l'utente
                    print("Opzioni disponibili:")
                    print("1. Mostra rubrica")
                    print("2. Aggiungi contatto")
                    print("3. Rimuovi contatto")
                    print("4. Avvia chat")
                    print("5. Avvia chat a tempo")
                    print("6. Attiva/Disattiva modalità 'non disturbare'")
                    print("7. Cerca utenti")
                    print("8. Logout")
                    # Chiede all'utente di inserire il numero dell'opzione desiderata
                    opzione = input("Inserisci il numero dell'opzione desiderata: ")

                    # Se l'utente sceglie l'opzione 1 (Mostra rubrica)
                    if opzione == '1':
                        # Pulisce lo schermo
                        clear_screen()
                        # Ottiene la lista dei contatti dell'utente
                        contatti = rubrica(username)
                        # Stampa l'intestazione della rubrica
                        print(f"Rubrica di {username}:")
                        # Ciclo per stampare ogni contatto nella rubrica
                        for contatto in contatti:
                            print(contatto)
                        # Chiede all'utente di premere INVIO per continuare
                        input("\nPremi INVIO per continuare...")

                    # Se l'utente sceglie l'opzione 2 (Aggiungi contatto)
                    elif opzione == '2':
                        # Chiede all'utente di inserire il nuovo contatto
                        nuovo_contatto = input("Inserisci un nuovo contatto: ")
                        # Verifica se l'utente esiste nel sistema
                        if r.exists(f"user:{nuovo_contatto}"):
                            # Verifica se il nuovo contatto non è già presente nella rubrica
                            if nuovo_contatto not in rubrica(username):
                                # Aggiunge il nuovo contatto alla rubrica
                                aggiungi_contatto(username, nuovo_contatto)
                                # Stampa un messaggio di conferma
                                print(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")
                            else:
                                # Stampa un messaggio di errore se il contatto è già presente
                                print(f"Errore!\nIl contatto {nuovo_contatto} è già presente nella rubrica.")
                                # Aspetta 3 secondi prima di continuare
                                time.sleep(3)
                        else:
                            # Stampa un messaggio di errore se l'utente non esiste nel sistema
                            print(f"Errore!\nIl contatto {nuovo_contatto} non è presente nel sistema.")
                            # Aspetta 3 secondi prima di continuare
                            time.sleep(3)

                    # Se l'utente sceglie l'opzione 3 (Rimuovi contatto)
                    elif opzione == '3':
                        # Chiede all'utente di inserire il contatto da rimuovere
                        contatto_da_rimuovere = input("Inserisci il contatto da rimuovere: ")
                        # Rimuove il contatto dalla rubrica
                        rimuovi_contatto(username, contatto_da_rimuovere)
                        # Stampa un messaggio di conferma
                        print(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

                    # Se l'utente sceglie l'opzione 4 (Avvia chat)
                    elif opzione == '4':
                        # Chiede all'utente di inserire il destinatario della chat
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica
                        if destinatario in rubrica(username):
                            # Avvia la chat con il destinatario
                            chat_messaggi(username, destinatario)
                        else:
                            # Stampa un messaggio di errore se il destinatario non è presente nella rubrica
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            # Aspetta 3 secondi prima di continuare
                            time.sleep(3)

                    # Se l'utente sceglie l'opzione 5 (Avvia chat a tempo)
                    elif opzione == '5':
                        # Chiede all'utente di inserire il destinatario della chat
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica
                        if destinatario in rubrica(username):
                            # Avvia la chat temporanea con il destinatario
                            chat_messaggi_temporanea(username, destinatario)
                        else:
                            # Stampa un messaggio di errore se il destinatario non è presente nella rubrica
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            # Aspetta 3 secondi prima di continuare
                            time.sleep(3)

                    # Se l'utente sceglie l'opzione 6 (Attiva/Disattiva modalità 'non disturbare')
                    elif opzione == '6':
                        # Attiva/disattiva la modalità 'non disturbare' per l'utente
                        toggle_dnd(username)

                    # Se l'utente sceglie l'opzione 7 (Cerca utenti)
                    elif opzione == '7':
                        # Chiede all'utente di inserire il nome utente (anche parziale)
                        parziale = input("Inserisci il nome utente (anche parziale): ")
                        # Cerca gli utenti che corrispondono alla stringa parziale
                        cerca_utenti(parziale)

                    # Se l'utente sceglie l'opzione 8 (Logout)
                    elif opzione == '8':
                        # Stampa un messaggio di conferma del logout
                        print(f"Logout effettuato per l'utente {username}.")
                        # Esce dal ciclo del menu dell'utente
                        break

                    # Se l'opzione inserita non è valida
                    else:
                        # Stampa un messaggio di errore
                        print("Opzione non valida. Riprova.")

        # Se l'utente sceglie l'opzione 2 (Esci)
        elif scelta == '2':
            # Stampa un messaggio di saluto
            print("Grazie per aver usato l'applicazione.")
            # Esce dal ciclo principale dell'applicazione
            break
        # Se l'opzione inserita non è valida
        else:
            # Stampa un messaggio di errore
            print("Opzione non valida. Riprova.")

# Punto di ingresso dell'applicazione
if __name__ == "__main__":
    # Avvia la sessione dell'applicazione
    avvia_sessione()
