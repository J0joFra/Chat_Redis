# Sistema di Chat con Redis

Questo progetto implementa un sistema di chat utilizzando Redis come database. Il sistema permette agli utenti di registrarsi, effettuare il login, gestire una rubrica di contatti, inviare messaggi in tempo reale e utilizzare una modalità "non disturbare". Di seguito sono riportate le istruzioni dettagliate per avviare il progetto da un'installazione pulita di Python 3.x.

## Prerequisiti

- Python 3.x installato sul sistema (preferibilmente Python 3.7 o superiore)
- Accesso a Internet per la connessione al database Redis remoto
- Conoscenza base dell'utilizzo del terminale o prompt dei comandi

## Passi dettagliati per l'avvio del progetto

1. **Preparazione dell'ambiente**:
   - Apri un terminale o prompt dei comandi.
   - Naviga alla directory in cui desideri clonare o scaricare il progetto:
     ```
     cd percorso/alla/tua/directory
     ```

2. **Clonazione del repository** (se applicabile):
   - Se il progetto è su un repository Git, clonalo con:
     ```
     git clone URL_DEL_REPOSITORY
     ```
   - Altrimenti, scarica il file del progetto e estrailo nella directory scelta.

3. **Creazione di un ambiente virtuale**:
   - Naviga nella directory del progetto:
     ```
     cd nome_directory_progetto
     ```
   - Crea un nuovo ambiente virtuale:
     ```
     python -m venv venv
     ```
   Questo comando creerà una nuova directory chiamata `venv` contenente l'ambiente virtuale.

4. **Attivazione dell'ambiente virtuale**:
   - Su Windows:
     ```
     venv\Scripts\activate
     ```
   - Su macOS e Linux:
     ```
     source venv/bin/activate
     ```
   Dovresti vedere il nome dell'ambiente virtuale all'inizio del prompt.

5. **Installazione delle dipendenze**:
   - Con l'ambiente virtuale attivato, installa le dipendenze necessarie:
     ```
     pip install redis colorama
     ```
   - Verifica che l'installazione sia andata a buon fine con:
     ```
     pip list
     ```
   Dovresti vedere `redis` e `colorama` nell'elenco dei pacchetti installati.

6. **Configurazione del file di progetto**:
   - Apri il file principale del progetto (presumibilmente chiamato `main.py`) con un editor di testo.
   - Individua la sezione di connessione a Redis, che dovrebbe essere simile a questa:
     ```python
     r = redis.Redis(host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
                     port=11602, db=0, charset="utf-8", decode_responses=True,
                     password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU")
     ```
   - Se necessario, modifica questi parametri con le credenziali fornite per il tuo database Redis.
   - Salva le modifiche al file.

7. **Esecuzione del progetto**:
   - Nel terminale, con l'ambiente virtuale ancora attivato, esegui:
     ```
     python main.py
     ```
   - Se il nome del file principale è diverso, sostituisci `main.py` con il nome corretto.

8. **Utilizzo del sistema di chat**:
   - Segui le istruzioni visualizzate nel terminale per navigare nel menu.
   - Per il primo utilizzo, scegli l'opzione di login e crea un nuovo account.
   - Esplora le varie funzionalità come l'aggiunta di contatti, l'invio di messaggi, ecc.

## Struttura del progetto

Il progetto è costituito principalmente da un singolo file Python che contiene tutte le funzionalità. Le principali componenti includono:

- Connessione e interazione con Redis
- Gestione degli utenti (login/registrazione)
- Gestione della rubrica
- Sistema di messaggistica in tempo reale
- Chat temporanea con timeout
- Modalità "non disturbare"

## Funzionalità dettagliate

1. **Login e Registrazione**:
   - Gli utenti possono creare un nuovo account o accedere con un account esistente.
   - Le password sono memorizzate in chiaro nel database Redis (nota: questa è una semplificazione e non è sicura per un ambiente di produzione).

2. **Gestione Rubrica**:
   - Gli utenti possono aggiungere o rimuovere contatti dalla propria rubrica.
   - La rubrica è memorizzata come una lista in Redis.

3. **Chat in tempo reale**:
   - Gli utenti possono inviare messaggi ad altri utenti presenti nella loro rubrica.
   - I messaggi sono memorizzati in Redis e recuperati in tempo reale.

4. **Chat temporanea**:
   - Funziona come la chat normale, ma viene automaticamente chiusa dopo 60 secondi di inattività.

5. **Modalità "Non Disturbare"**:
   - Gli utenti possono attivare questa modalità per non ricevere messaggi.

6. **Ricerca Utenti**:
   - È possibile cercare utenti nel sistema utilizzando una stringa parziale del nome utente.

## Risoluzione dei problemi comuni

1. **Errore di connessione a Redis**:
   - Verifica che le credenziali di Redis siano corrette.
   - Assicurati di avere una connessione internet stabile.
   - Controlla che il servizio Redis sia accessibile dalla tua rete.

2. **Errori di importazione dei moduli**:
   - Assicurati di aver installato correttamente tutte le dipendenze.
   - Verifica che l'ambiente virtuale sia attivato.

3. **Problemi di visualizzazione dei colori**:
   - Su Windows, potrebbero esserci problemi con la visualizzazione dei colori. Prova a eseguire `python -m colorama.initialise` prima di avviare il programma.



