'''
Il software deve consentire ad un utente di registrarsi sul sistema indicando nome utente (univoco) e password.
Non è concessa la registrazione di due utenti con lo stesso nome
Dopo la login l’utente ha disposizione le seguenti funzionalità:
Ricerca di altri utenti a sistema attraverso il nome utente (anche parziale)
Aggiunta di un utente alla propria lista contatti
Impostazione della modalità Do Not Disturb
Invio di messaggi ad altri utenti presenti nella propria lista contatti
Se il messaggio sta venendo inviato ad un utente che è un modalità “Do Not Disturb”:
il messaggio non viene recapitato e il sistema mostra un errore

Lettura dei messaggi (inviati e ricevuti) presenti in una chat con un utente specifico.
I messaggi devono essere ordinati per data e istante di invio, con i messaggi più recenti in coda.
I messaggi inviati devono essere mostrati con un > come prefisso, quelli ricevuti con un  < come prefisso.

Segue un esempio di output:

>> Chat con gino <<

> Tutto bene	[2023-12-06 10:50:05]
< Come va?		[2023-12-06 10:50:04]
> Molto!		[2023-12-06 10:50:00]
< Bella questa chat! [2023-12-06 10:40:30]
!! IMPOSSIBILE RECAPITARE IL MESSAGGIO, L’uTENTE HA LA MODALITA’ DnD ATTIVA
> 123 Prova! [2023-12-06 10:30:00]
Requisiti opzionali
Implementare la possibilità di ricevere delle notifiche push sulla chat, la schermata di cui al punto (e) deve quindi aggiornare in tempo “reale” non appena viene inviato un messaggio (3/30)
Implementare la possibilità di iniziare una chat “a tempo” con un utente, tale chat  dovrà distruggersi entro 1 minuto dall’ultimo messaggio inviato. (1/30)



'''





import redis




r = redis.Redis(host='172.17.33.111', port=6380,password="miao", db=0, charset="utf-8", decode_responses=True)

#funzione per la creazione di un nuovo account
def register_user(username, password):
    # Controlla se l'utente esiste già
    if r.hexists('users', username):
        return f"Errore: Il nome utente '{username}' esiste già."
    
    # Registra il nuovo utente
    r.hset('users', username, password)
    return f"Utente '{username}' registrato con successo."

if __name__ == "__main__":
    while True:
        print("Sistema di registrazione utenti")
        username = input("Inserisci il nome utente: ")
        password = input("Inserisci la password: ")

        # Registra l'utente
        result = register_user(username, password)
        print(result)