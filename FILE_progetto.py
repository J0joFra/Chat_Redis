import redis
import threading
import time
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Connessione a Redis
try:
    r = redis.Redis(host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
                    port=11602, db=0, charset="utf-8", decode_responses=True,
                    password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU")
    r.ping()
except redis.ConnectionError as e:
    print(f"Errore di connessione a Redis: {e}")
    exit(1)

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def login(username):
    while True:
        if r.exists(username):
            user_data = r.hgetall(username)
            clear_screen()
            password = input(f"Username: {username}\nInserisci la password: ")
            if user_data.get("password") == password:
                return user_data
            else:
                clear_screen()
                print("Password errata.")
        else:
            password = input("Crea una nuova password: ")
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hset(username, mapping=user_data)
            return user_data

def rubrica(username):
    rubrica_key = f"{username}_rubrica"
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)
    contatti = r.lrange(rubrica_key, 0, -1)
    return contatti

def aggiungi_contatto(username, nuovo_contatto):
    clear_screen()
    rubrica_key = f"{username}_rubrica"
    r.rpush(rubrica_key, nuovo_contatto)

def rimuovi_contatto(username, contatto_da_rimuovere):
    clear_screen()
    rubrica_key = f"{username}_rubrica"
    r.lrem(rubrica_key, 0, contatto_da_rimuovere)

def chat_messaggi(mittente, destinatario):
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    destinatario_data = r.hgetall(destinatario)
    
    def aggiorna_chat():
        last_shown_index = 0
        try:
            while True:
                messaggi = r.lrange(chat_key, 0, -1)
                new_messages = messaggi[last_shown_index:]
                if new_messages:
                    for messaggio in new_messages:
                        timestamp = messaggio[-5:]
                        if messaggio.startswith(f"{mittente}: "):
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-5]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            if messaggio.startswith("\u00b7 "):
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-5]}\n{timestamp}")
                    last_shown_index += len(new_messages)
                time.sleep(1)
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")
    
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    
    while True:
        messaggio = input()
        if messaggio.strip().lower() == 'exit':
            break
        timestamp = datetime.now().strftime('%H:%M')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        if destinatario_data.get("dnd") == "True":
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key, messaggio_formattato)

def chat_messaggi_temporanea(mittente, destinatario):
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}_temp"
    destinatario_data = r.hgetall(destinatario)
    chat_attiva = True

    def aggiorna_chat():
        clear_screen()
        last_shown_index = 0
        try:
            while chat_attiva:
                messaggi = r.lrange(chat_key, 0, -1)
                new_messages = messaggi[last_shown_index:]
                if new_messages:
                    for messaggio in new_messages:
                        timestamp = messaggio[-8:]
                        if messaggio.startswith(f"{mittente}: "):
                            msg = "\u00b7 " + messaggio[len(mittente) + 2:-8]
                            print(f"{Fore.LIGHTYELLOW_EX + msg.rjust(80)}\n{timestamp.rjust(80)}")
                        else:
                            if messaggio.startswith("\u00b7 "):
                                print(f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX + messaggio.rjust(80)}\n{timestamp.rjust(80)}")
                            else:
                                print(f"{Style.BRIGHT}{Fore.GREEN}{messaggio[:-8]}\n{timestamp}")
                    last_shown_index += len(new_messages)
                time.sleep(1)
        except Exception as e:
            print(f"Errore durante l'aggiornamento della chat: {e}")

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
                    r.delete(chat_key)
                    clear_screen()
                    print(f"\nLa chat tra {mittente} e {destinatario} è stata eliminata per inattività.")
                    time.sleep(5)
                    print("Premi INVIO per continuare...")
                    return True
        except Exception as e:
            print(f"Errore durante il monitoraggio della chat: {e}")
            return False
    
    threading.Thread(target=aggiorna_chat, daemon=True).start()
    monitor_thread = threading.Thread(target=monitor_chat_timeout)
    monitor_thread.start()

    while True:
        if not monitor_thread.is_alive():
            break

        messaggio = input()
        if messaggio.strip().lower() == 'exit':
            break
        timestamp = datetime.now().strftime('%H:%M:%S')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        if destinatario_data.get("dnd") == "True":
            print("Errore!\nMessaggio non recapitato perché il destinatario è in modalità non disturbare.")
        else:
            r.rpush(chat_key, messaggio_formattato)      

    chat_attiva = False
    r.delete(chat_key)
    print(f"\nLa chat tra {mittente} e {destinatario} è stata chiusa.")
    time.sleep(2)

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

def cerca_utenti(parziale):
    clear_screen()
    chiavi = r.keys()
    risultati = []
    for chiave in chiavi:
        if parziale in chiave and ':' not in chiave:
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
                    print("5. Avvia chat a tempo")
                    print("6. Attiva/Disattiva modalità 'non disturbare'")
                    print("7. Cerca utenti")
                    print("8. Logout")
                    opzione = input("Inserisci il numero dell'opzione desiderata: ")

                    if opzione == '1':
                        clear_screen()
                        contatti = rubrica(username)
                        print(f"Rubrica di {username}:")
                        for contatto in contatti:
                            print(contatto)
                        input("\nPremi INVIO per continuare...")

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
                        destinatario = input("Inserisci il destinatario della chat: ")
                        if destinatario in rubrica(username):
                            chat_messaggi_temporanea(username, destinatario)
                        else:
                            print(f"Errore!\nIl destinatario {destinatario} non è presente nella rubrica.")
                            time.sleep(3)

                    elif opzione == '6':
                        toggle_dnd(username)

                    elif opzione == '7':
                        parziale = input("Inserisci il nome utente (anche parziale): ")
                        cerca_utenti(parziale)

                    elif opzione == '8':
                        print(f"Logout effettuato per l'utente {username}.")
                        break

                    else:
                        print("Opzione non valida. Riprova.")

        elif scelta == '2':
            print("Grazie per aver usato l'applicazione.")
            break
        else:
            print("Opzione non valida. Riprova.")

if __name__ == "__main__":
    avvia_sessione()
