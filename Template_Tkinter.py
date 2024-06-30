import streamlit as st
import redis
import time
from datetime import datetime

# Connessione a Redis
try:
    r = redis.Redis(
        host='redis-11602.c304.europe-west1-2.gce.redns.redis-cloud.com',
        port=11602, db=0, charset="utf-8", decode_responses=True,
        password="aoabFoYLlhgn4EzDNPwtre5RoFGgCNiU"
    )
    r.ping()
except redis.ConnectionError as e:
    st.error(f"Errore di connessione a Redis: {e}")
    st.stop()

def login(username):
    if r.exists(username):
        password = st.text_input("Inserisci la password:", type="password")
        user_data = r.hgetall(username)
        if st.button("Login", key=f"login_{username}"):
            if user_data.get("password") == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["user_data"] = user_data
            else:
                st.error("Password errata.")
    else:
        password = st.text_input("Crea una nuova password:", type="password")
        if st.button("Registrati", key=f"register_{username}"):
            user_data = {"username": username, "password": password, "dnd": "False"}
            r.hset(username, mapping=user_data)
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["user_data"] = user_data

def mostra_rubrica(username):
    rubrica_key = f"{username}_rubrica"
    if not r.exists(rubrica_key):
        r.rpush(rubrica_key, username)
    contatti = r.lrange(rubrica_key, 0, -1)
    st.write("La tua rubrica:")
    for contatto in contatti:
        st.write(f"- {contatto}")

def aggiungi_contatto(username):
    nuovo_contatto = st.text_input("Inserisci un nuovo contatto:")
    if st.button("Aggiungi", key=f"aggiungi_contatto_{username}"):
        if r.exists(nuovo_contatto):
            if nuovo_contatto not in r.lrange(f"{username}_rubrica", 0, -1):
                r.rpush(f"{username}_rubrica", nuovo_contatto)
                st.success(f"Contatto {nuovo_contatto} aggiunto alla rubrica.")
            else:
                st.error(f"Il contatto {nuovo_contatto} è già presente nella rubrica.")
        else:
            st.error(f"Il contatto {nuovo_contatto} non è presente nel sistema.")

def rimuovi_contatto(username):
    contatto_da_rimuovere = st.text_input("Inserisci il contatto da rimuovere:")
    if st.button("Rimuovi", key=f"rimuovi_contatto_{username}"):
        r.lrem(f"{username}_rubrica", 0, contatto_da_rimuovere)
        st.success(f"Contatto {contatto_da_rimuovere} rimosso dalla rubrica.")

def chat_messaggi(mittente, destinatario):
    lista = [mittente, destinatario]
    lista.sort()
    chat_key = f"{lista[0]}_{lista[1]}"
    
    # Recupera i messaggi dal database
    messaggi = r.lrange(chat_key, 0, -1)
    
    # Crea un contenitore per la chat
    chat_container = st.container()
    
    # Crea un form per l'input del messaggio
    with st.form(key=f"message_form_{mittente}_{destinatario}"):
        col1, col2 = st.columns([4, 1])
        with col1:
            messaggio = st.text_input("Scrivi un messaggio:", key=f"message_input_{mittente}_{destinatario}")
        with col2:
            invia = st.form_submit_button("Invia")
    
    if invia and messaggio:
        timestamp = datetime.now().strftime('%H:%M')
        messaggio_formattato = f"{mittente}: {messaggio} {timestamp}"
        r.rpush(chat_key, messaggio_formattato)
        messaggi.append(messaggio_formattato)
    
    # Visualizza i messaggi
    with chat_container:
        st.markdown("""
        <style>
        .chat-container {
            background-color: #E5DDD5;
            padding: 20px;
            border-radius: 10px;
            height: 400px;
            overflow-y: auto;
        }
        .chat-message {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: inline-block;
            max-width: 70%;
            word-wrap: break-word;
        }
        .sender {
            background-color: #DCF8C6;
            float: right;
            clear: both;
        }
        .receiver {
            background-color: #FFFFFF;
            float: left;
            clear: both;
        }
        .timestamp {
            font-size: 0.8em;
            color: #888;
            display: block;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for messaggio in messaggi:
            parti = messaggio.split(': ', 1)
            if len(parti) == 2:
                sender, content = parti
                timestamp = content[-5:]
                content = content[:-6]  # Rimuovi il timestamp dal contenuto
                
                if sender == mittente:
                    st.markdown(f"""
                    <div class="chat-message sender">
                        {content}
                        <span class="timestamp">{timestamp}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message receiver">
                        {content}
                        <span class="timestamp">{timestamp}</span>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll automatico alla fine della chat
        st.markdown('<div id="end-of-chat"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
            var chatContainer = document.querySelector('.chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
        """, unsafe_allow_html=True)

def toggle_dnd(username):
    user_data = r.hgetall(username)
    dnd_status = user_data.get("dnd", "False")
    new_dnd_status = "False" if dnd_status == "True" else "True"
    r.hset(username, "dnd", new_dnd_status)
    if new_dnd_status == 'True':
        st.success("Modalità 'non disturbare' attivata")
    else:
        st.success("Modalità 'non disturbare' disattivata")

def cerca_utenti(parziale):
    chiavi = r.keys()
    risultati = []
    for chiave in chiavi:
        if parziale in chiave and ':' not in chiave:
            if r.type(chiave) == 'hash':
                risultati.append(chiave)
    
    if risultati:
        st.write("Risultati della ricerca:")
        for utente in risultati:
            st.write(utente)
    else:
        st.write("Nessun utente trovato.")

def avvia_sessione():
    st.set_page_config(page_title="WhatsApp-like Chat", layout="wide")
    
    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">WhatsApp-like Chat</p>', unsafe_allow_html=True)

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username:")
        with col2:
            if username:
                login(username)
    else:
        st.sidebar.success(f"Benvenuto, {st.session_state['username']}!")
        opzione = st.sidebar.selectbox("Opzioni", [
            "Mostra rubrica", "Aggiungi contatto", "Rimuovi contatto",
            "Avvia chat", "Attiva/Disattiva modalità 'non disturbare'", "Cerca utenti", "Logout"
        ])
        
        if opzione == "Mostra rubrica":
            mostra_rubrica(st.session_state["username"])

        elif opzione == "Aggiungi contatto":
            aggiungi_contatto(st.session_state["username"])

        elif opzione == "Rimuovi contatto":
            rimuovi_contatto(st.session_state["username"])

        elif opzione == "Avvia chat":
            destinatario = st.text_input("Inserisci il destinatario della chat:")
            if destinatario and st.button("Avvia", key=f"avvia_chat_{destinatario}"):
                if destinatario in r.lrange(f"{st.session_state['username']}_rubrica", 0, -1):
                    st.session_state["current_chat"] = destinatario
                else:
                    st.error(f"Il destinatario {destinatario} non è presente nella rubrica.")

        elif opzione == "Attiva/Disattiva modalità 'non disturbare'":
            toggle_dnd(st.session_state["username"])

        elif opzione == "Cerca utenti":
            parziale = st.text_input("Inserisci il nome utente (anche parziale):")
            if st.button("Cerca", key="cerca_utenti"):
                cerca_utenti(parziale)

        elif opzione == "Logout":
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["user_data"] = {}
            st.session_state["current_chat"] = None
            st.sidebar.success("Logout effettuato.")
            st.experimental_rerun()

        if st.session_state.get("current_chat"):
            st.subheader(f"Chat con {st.session_state['current_chat']}")
            chat_messaggi(st.session_state["username"], st.session_state["current_chat"])

if __name__ == "__main__":
    avvia_sessione()