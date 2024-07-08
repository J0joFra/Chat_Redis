# Progetto di esame REDIS BD 2023
Software di messaggistica stile “Whatsapp”
CONSEGNA: 01/07/24

## Regole generali
- Il progetto va realizzato e consegnato secondo i gruppi indicati
- Il software deve essere sviluppato in Python
- Il software deve essere consegnato come repository git su GitHub, anche pubblica. Se si vuole fare un repository privato aggiungere questi utenti come come membri del progetto: **@nanomad** & **@danidemi**

Nel repository git deve essere presente un file README che descrive, passo passo, come avviare il progetto da una installazione *pulita* di python 3.x
- Indicate chiaramente eventuali file da modificare per inserire credenziali o altro
- Indicate nel README eventuali semplificazioni o assunzioni che avete fatto rispetto alla consegna originale del progetto
- Va realizzato un breve video (max 5’) che commenta il codice e dimostra il funzionamento del programma.
- Creare una cartella nelle consegne 
- nome della cartella = membri del gruppo, es “rossi brambilla esposito”
- caricare video o link a file video
- caricare URL del repo Git

## Requisiti obbligatori
Il software deve consentire ad un utente di registrarsi sul sistema indicando nome utente (univoco) e password. Non è concessa la registrazione di due utenti con lo stesso nome
-Dopo la login l’utente ha disposizione le seguenti funzionalità:
a. Ricerca di altri utenti a sistema attraverso il nome utente (anche parziale)
b. Aggiunta di un utente alla propria lista contatti
c. Impostazione della modalità Do Not Disturb
d. Invio di messaggi ad altri utenti presenti nella propria lista contatti
i. Se il messaggio sta venendo inviato ad un utente che è un modalità “Do Not Disturb”, il messaggio non viene recapitato e il sistema mostra un errore
e. Lettura dei messaggi (inviati e ricevuti) presenti in una chat con un utente specifico. I messaggi devono essere ordinati per data e istante di invio, con i messaggi più recenti in coda. I messaggi inviati devono essere mostrati con un > come prefisso, quelli ricevuti con un  < come prefisso. 

## Requisiti opzionali
- Implementare la possibilità di ricevere delle notifiche push sulla chat, la schermata di cui al punto (e) deve quindi aggiornare in tempo “reale” non appena viene inviato un messaggio (3/30)
- Implementare la possibilità di iniziare una chat “a tempo” con un utente, tale chat  dovrà distruggersi entro 1 minuto dall’ultimo messaggio inviato. (1/30)