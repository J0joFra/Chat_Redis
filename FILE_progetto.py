#region Importazioni
import redis 
import threading 
import time
import os 
from datetime import datetime
from colorama import Fore, Style, init 

# Inizializza il modulo colorama per utilizzare i colori nella console
init(autoreset=True)

#region Connessione a Redis
try: #-> server di Jo (prima usato quello di Giu)
    r = redis.Redis(host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
                    port=11602, db=0, charset="utf-8", decode_responses=True,
                    password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU") #Istanza del client Redis con le credenziali fornite
    r.ping() # Verifica la connessione a Redis
except redis.ConnectionError as e:
    print(f"Errore di connessione a Redis: {e}") #Errore di connessione a Redis
    exit(1)

#region Pulire la console
def clear_screen():
    if os.name == 'nt': # Windows
        os.system('cls') 
    else:
        os.system('clear') #no Windows

#region Login
def login(username):
    while True:
        if r.exists(f"user:{username}"): # Controlla se l'utente esiste nel database
            user_data = r.hgetall(f"user:{username}") # Ottiene i dati dell'utente dal database
            clear_screen()
            password = input(f"Username: {username}\nInserisci la password: ")
            if user_data.get("password") == password: # Controlla se la password inserita è corretta
                return user_data 
            else:
                clear_screen()
                print("Password errata.") 
        else: # Nuova password
            password = input("Crea una nuova password: ") 
            user_data = {"username": username, "password": password, "dnd": "False"} # Crea un dizionario con i dati dell'utente
            r.hset(f"user:{username}", mapping=user_data) # Salva i dati dell'utente nel database
            return user_data # Restituisce i dati dell'utente

#region Mostra Rubrica
def rubrica(username):
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    if not r.exists(rubrica_key): 
        r.rpush(rubrica_key, username) #Crea una nuova rubrica con l'username dell'utente
    contatti = r.lrange(rubrica_key, 0, -1) # Ottiene la lista dei contatti dalla rubrica
    return contatti # Restituisce la lista dei contatti

#region Add Contatto
def aggiungi_contatto(username, nuovo_contatto):
    clear_screen()
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    r.rpush(rubrica_key, nuovo_contatto) # Aggiunge il nuovo contatto alla rubrica

#region Rimuovere Contatto
def rimuovi_contatto(username, contatto_da_rimuovere):
    clear_screen()
    rubrica_key = f"rubrica:{username}" # Crea la chiave per la rubrica dell'utente
    r.lrem(rubrica_key, 0, contatto_da_rimuovere) # Rimuove il contatto dalla rubrica

#region Chat Messaggi
def chat_messaggi(mittente, destinatario):
    lista = sorted([mittente, destinatario]) # Ordina gli username in ordine alfabetico
    chat_key1 = f"chat:{lista[0]}:{lista[1]}" # Crea la chiave per la chat tra i due utenti
    chat_key2 = f"chat:{lista[1]}:{lista[0]}" # Crea la chiave per la chat tra i due utenti (invertita)
    destinatario_data = r.hgetall(f"user:{destinatario}") 

    #Cartella Chat
    def crea_cartelle_chat():
        if not r.exists(chat_key1): # Controlla se la chat esiste nel database
            r.rpush(chat_key1, "") 
        if not r.exists(chat_key2):
            r.rpush(chat_key2, "") 

    crea_cartelle_chat() # Crea le cartelle per la chat

    #aggiorna chat
    def aggiorna_chat():
        last_shown_index = 0 # Indice dell'ultimo messaggio mostrato
        try:
            while True:
                messaggi = r.lrange(chat_key1, 0, -1) #Lista dei messaggi dalla chat
                new_messages = messaggi[last_shown_index:] #Nuovi messaggi dalla lista
                if new_messages:
                    for messaggio in new_messages:
                        timestamp = messaggio[-5:] # Ottiene l'orario del messaggio
                        if messaggio.startswith(f"{mittente}: "): # Se il messaggio è stato inviato dal mittente
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-5]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}") # Messaggio con il colore giallo
                        else:
                            if messaggio.startswith("\u00b7 "): # Se il messaggio è una risposta
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-5]}\n{timestamp}") # Messaggio con il colore verde
                    last_shown_index += len(new_messages) # Aggiorna l'indice dell'ultimo messaggio mostrato
                time.sleep(1) 
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")

    threading.Thread(target=aggiorna_chat, daemon=True).start() # Avvia un nuovo thread per aggiornare la chat

    while True:
        messaggio = input()
        if messaggio.strip().lower() == 'exit': # Se l'utente inserisce 'exit', esce dal ciclo
            break
        timestamp = datetime.now().strftime('%H:%M') # Ottiene l'orario attuale
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}" # Formatta il messaggio con l'username e l'orario
        if destinatario_data.get("dnd") == "True": # Controlla la modalità 'non disturbare'
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key1, messaggio_formattato) # Aggiunge il messaggio alla chat
            r.rpush(chat_key2, messaggio_formattato) # Aggiunge il messaggio alla chat (invertita)

#region Chat a tempo
def chat_messaggi_temporanea(mittente, destinatario):
    lista = sorted([mittente, destinatario])
    chat_key1 = f"chat_temp:{lista[0]}:{lista[1]}"
    chat_key2 = f"chat_temp:{lista[1]}:{lista[0]}"
    destinatario_data = r.hgetall(f"user:{destinatario}")   # Dati dell'utente destinatario
    chat_attiva = True    # Chat impostata come attiva

    def crea_cartelle_chat():
        if not r.exists(chat_key1):
            r.rpush(chat_key1, "")
        if not r.exists(chat_key2):
            r.rpush(chat_key2, "")

    crea_cartelle_chat()

    #aggiornare la chat
    def aggiorna_chat():
        clear_screen()
        last_shown_index = 0
        try:
            # Ciclo che continua finché la chat è attiva
            while chat_attiva:
                messaggi = r.lrange(chat_key1, 0, -1) #Lista dei messaggi dalla chat
                new_messages = messaggi[last_shown_index:] #Nuovi messaggi dalla lista
                if new_messages:
                    for messaggio in new_messages:
                        timestamp = messaggio[-8:] # Ottiene l'orario del messaggio
                        if messaggio.startswith(f"{mittente}: "): #Se inviato dal mittente
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-8]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            if messaggio.startswith("\u00b7 "): #inviato dal mittente in orecedenza
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-8]}\n{timestamp}") #messaggio del destinatario
                    last_shown_index += len(new_messages)  # Aggiorna l'indice dell'ultimo messaggio mostrato
                time.sleep(1)
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")

    #Monitorare il timeout della chat
    def monitor_chat_timeout():
        timeout_seconds = 0
        try:
            while chat_attiva: #finchè la chat è attiva
                start_time = time.time() #tempo iniziale
                while chat_attiva:
                    time.sleep(1)
                    elapsed_time = time.time() - start_time  #Tempo trascorso

                    if elapsed_time >= 60:
                        timeout_seconds += elapsed_time #Aggiorna il contatore del timeout
                        break
                    if r.llen(chat_key1) > 0: #Nuovi messaggi nella chat
                        timeout_seconds = 0 #Resetta contatore

                # Se il timeout è scaduto
                if timeout_seconds >= 60:
                    r.delete(chat_key1) #Elimina la chat dal database
                    r.delete(chat_key2)
                    
                    clear_screen()
                    print(f"\nLa chat tra {mittente} e {destinatario} è stata eliminata per inattività.")
                    time.sleep(5)
                    print("Premi INVIO per continuare...")
                    return True
        except Exception as e:
            print(f"Errore durante il monitoraggio della chat: {e}")
            return False

    #Avvia un nuovo thread per aggiornare la chat
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    #Avvia un nuovo thread per monitorare il timeout della chat
    monitor_thread = threading.Thread(target=monitor_chat_timeout)
    monitor_thread.start()

    # Ciclo principale per inviare messaggi
    while True:
        # Se il thread di monitoraggio del timeout è terminato
        if not monitor_thread.is_alive():
            break

        messaggio = input()
        if messaggio.strip().lower() == 'exit':
            break
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Formatta il messaggio <giovanni: ciao 23:48:27>
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        
        if destinatario_data.get("dnd") == "True":
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key1, messaggio_formattato)   # Aggiunge il messaggio alla chat
            r.rpush(chat_key2, messaggio_formattato)

    #Chat impostata come non attiva
    chat_attiva = False
    # Elimina le chiavi della chat dal database
    r.delete(chat_key1)
    r.delete(chat_key2)
    print(f"\nLa chat tra {mittente} e {destinatario} è stata chiusa.")
    time.sleep(2)

#region Modalità dnd
def toggle_dnd(username):
    user_data = r.hgetall(f"user:{username}")
    # Ottiene lo stato attuale della modalità 'non disturbare'
    dnd_status = user_data.get("dnd", "False")
    # Imposta il nuovo stato della modalità 'non disturbare'
    new_dnd_status = "False" if dnd_status == "True" else "True"
    # Aggiorna lo stato della modalità 'non disturbare' nel database
    r.hset(f"user:{username}", "dnd", new_dnd_status)
    clear_screen()
    
    # Stampa un messaggio di notifica
    if new_dnd_status == 'True':
        print("Modalità 'non disturbare' attivata")
    else:
        print("Modalità 'non disturbare' disattivata")
    time.sleep(2)

#region Cercare utenti
def cerca_utenti(parziale):
    clear_screen()
    # Ottiene tutte le chiavi che iniziano con "user:"
    chiavi = r.keys("user:*")
    risultati = []
    # Ciclo per ogni chiave
    for chiave in chiavi:
        # Se la chiave contiene la stringa parziale
        if parziale in chiave:
            # Aggiunge l'username alla lista dei risultati
            risultati.append(chiave.split(":")[1])
    
    # Se ci sono risultati
    if risultati:
        print("Risultati della ricerca:")
        # Ciclo per ogni risultato
        for utente in risultati:
            print(utente)
    else:
        print("Nessun utente trovato.")
    input("\nPremi INVIO per continuare...")

#region Avvia sessione
def avvia_sessione():
    # Ciclo infinito per mantenere l'applicazione in esecuzione
    while True:
        clear_screen()
        # Stampa le opzioni disponibili per l'utente
        print("Opzioni disponibili:")
        print("1. Login")
        print("2. Esci")
        # Chiede all'utente di inserire il numero dell'opzione desiderata
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        # Se l'utente sceglie l'opzione 1 (Login)
        if scelta == '1':
            username = input("Username: ")
            # Esegue la funzione di login con l'username inserito
            user_data = login(username)

            if user_data:   # Se il login ha avuto successo (user_data non è vuoto)
                
                #loading Section
                loading = 0
                print(f"Benvenuto, {username}!")
                # Imposta la larghezza della barra di caricamento
                width = 50
                for i in range(101):
                    # Calcola la lunghezza della barra di caricamento
                    progress = "=" * int(width * i / 100)
                    # Calcola gli spazi vuoti rimanenti
                    spaces = " " * (width - len(progress))
                    print(f"\rLoading: [{progress}{spaces}] {i}%", end="", flush=True)
                    # Aspetta 0.02 secondi prima di aggiornare la barra di caricamento
                    time.sleep(0.02)
                print("\nLoading complete!")
               
                # Ciclo infinito per mantenere il menu dell'utente in esecuzione
                while True:
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

                    # (Mostra rubrica)
                    if opzione == '1':
                        clear_screen()
                        # Ottiene la lista dei contatti dell'utente
                        contatti = rubrica(username)
                        print(f"Rubrica di {username}:")
                        
                        for contatto in contatti:
                            print(contatto)
                        input("\nPremi INVIO per continuare...")

                    # (Aggiungi contatto)
                    elif opzione == '2':
                        nuovo_contatto = input("Inserisci un nuovo contatto: ")
                        # Verifica se l'utente esiste nel sistema
                        if r.exists(f"user:{nuovo_contatto}"):
                            # Verifica se il nuovo contatto non è già presente nella rubrica
                            if nuovo_contatto not in rubrica(username):
                                aggiungi_contatto(username, nuovo_contatto)
                                print(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")
                            else:
                                print(f"Errore!\nIl contatto {nuovo_contatto} è già presente nella rubrica.")
                                time.sleep(3)
                        else:
                            #Se l'utente non esiste nel sistema
                            print(f"Errore!\nIl contatto {nuovo_contatto} non è presente nel sistema.")
                            time.sleep(3)

                    #(Rimuovi contatto)
                    elif opzione == '3':
                        contatto_da_rimuovere = input("Inserisci il contatto da rimuovere: ")
                        rimuovi_contatto(username, contatto_da_rimuovere)
                        print(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

                    # (Avvia chat)
                    elif opzione == '4':
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica
                        if destinatario in rubrica(username):
                            chat_messaggi(username, destinatario)
                        else:
                            #Se il destinatario non è presente nella rubrica
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    # (Avvia chat a tempo)
                    elif opzione == '5':
                        destinatario = input("Inserisci il destinatario della chat: ")
                        # Verifica se il destinatario è presente nella rubrica
                        if destinatario in rubrica(username):
                            chat_messaggi_temporanea(username, destinatario)
                        else:
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    # (Attiva/Disattiva modalità 'non disturbare')
                    elif opzione == '6':
                        toggle_dnd(username)

                    # (Cerca utenti)
                    elif opzione == '7':
                        parziale = input("Inserisci il nome utente (anche parziale): ")
                        cerca_utenti(parziale)

                    # (Logout)
                    elif opzione == '8':
                        print(f"Logout effettuato per l'utente {username}.")
                        break

                    # Se l'opzione inserita non è valida
                    else:
                        # Stampa un messaggio di errore
                        print("Opzione non valida. Riprova.")

        # (Esci)
        elif scelta == '2':
            print("Grazie per aver usato l'applicazione.")
            # Esce dal ciclo principale dell'applicazione
            break
        # Se l'opzione inserita non è valida
        else:
            # Stampa un messaggio di errore
            print("Opzione non valida. Riprova.")

#region Punto di ingresso dell'applicazione
if __name__ == "__main__":
    avvia_sessione()
