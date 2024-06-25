import redis
import threading
import time
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)  # Inizializza colorama

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
            user_data = r.hgetall(username)  # Get di tutti gli username
            clear_screen()
            password = input(f"Username: {username}\nInserisci la password: ")
            if user_data.get("password") == password:
                return user_data
            else:
                clear_screen()
                print("Password errata.")
        else:  # Username non esistente
            password = input("Crea una nuova password: ")
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hset(username, mapping=user_data)
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
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    
    destinatario_data = r.hgetall(destinatario)
    
    def aggiorna_chat():
        last_shown_index = 0
        while True:
            messaggi = r.lrange(chat_key, 0, -1)
            new_messages = messaggi[last_shown_index:]
            if new_messages:
                for messaggio in new_messages:
                    if messaggio.startswith(f"{mittente}: "):
                        msg, timestamp = messaggio.rsplit(' ', 1)
                        msg = "\u00b7 "+msg[len(mittente) + 2:]
                        print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                    else:
                        if messaggio.startswith("\u00b7 "):  # messaggio mittente vecchio
                            print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                        else:  # messaggio destinatario
                            print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio}")
                last_shown_index += len(new_messages)
            time.sleep(1)  # Riduco il delay per aggiornamenti più frequenti
    
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    
    while True:
        messaggio = input()  # Solo input del messaggio, senza prompt
        if messaggio.strip().lower() == 'exit':
            break
        timestamp = datetime.now().strftime('%H:%M')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"  # Formato messaggio con il timestamp
        if destinatario_data.get("dnd") == "True":
            print(f"Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key, messaggio_formattato)

# Funzione per attivare/disattivare la modalità non disturbare
def toggle_dnd(username):
    user_data = r.hgetall(username)
    dnd_status = user_data.get("dnd", "False")
    new_dnd_status = "False" if dnd_status == "True" else "True"
    r.hset(username, "dnd", new_dnd_status)
    clear_screen()
    if new_dnd_status == 'True':
        print("Modalità 'non disturbare' attivata")
    else:
        print("Modalità 'non disturbare' disattivata")
    time.sleep(2)

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
            user_data = login(username)
            if user_data:
                loading = 0
                print(f"Benvenuto, {username}!")
                width = 50
                for i in range(101):
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
                    print("5. Attiva/Disattiva modalità 'non disturbare'")
                    print("6. Logout")
                    opzione = input("Inserisci il numero dell'opzione desiderata: ")

                    if opzione == '1':
                        clear_screen()
                        contatti = rubrica(username)
                        print(f"Rubrica di {username}:")
                        for contatto in contatti:
                            print(contatto)
                        time.sleep(10)

                    elif opzione == '2':
                        nuovo_contatto = input("Inserisci un nuovo contatto: ")
                        if r.exists(nuovo_contatto):
                            if nuovo_contatto not in rubrica(username):
                                aggiungi_contatto(username, nuovo_contatto)
                                print(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")
                            else:
                                print(f"Errore!\nIl contatto {nuovo_contatto} è già presente nella rubrica.")
                                time.sleep(3)
                        else:
                            print(f"Errore!\nIl contatto {nuovo_contatto} non è presente nel sistema.")
                            time.sleep(3)

                    elif opzione == '3':
                        contatto_da_rimuovere = input("Inserisci il contatto da rimuovere: ")
                        rimuovi_contatto(username, contatto_da_rimuovere)
                        print(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

                    elif opzione == '4':
                        destinatario = input("Inserisci il destinatario della chat: ")
                        if destinatario in rubrica(username):
                            chat_messaggi(username, destinatario)
                        else:
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    elif opzione == '5':
                        toggle_dnd(username)

                    elif opzione == '6':
                        print(f"Logout effettuato per l'utente {username}.")
                        break

                    else:
                        print("Opzione non valida. Riprova.")

        elif scelta == '2':
            print("Grazie per aver usato l'applicazione.")
            break
        else:
            print("Opzione non valida. Riprova.")

# Avvio del programma
if __name__ == "__main__":
    avvia_sessione()
