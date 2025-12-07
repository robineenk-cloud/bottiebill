import streamlit as st
import pandas as pd
from services.service import ChatbotService
import time

# Initialize chatbot service
@st.cache_resource
def get_chatbot():
    return ChatbotService()

chatbot = get_chatbot()

# Page config
st.set_page_config(
    page_title="Billie Bot - Klantenservice Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Sidebar voor extra functionaliteit
with st.sidebar:
    st.header("📊 Billie Info")
    st.write("""
    **Wat kan ik voor je doen?**
    - 📦 Pakket status opvragen
    - 🔄 Retour informatie
    - 💰 Betalingsvragen
    - 📝 Bestelinfo
    - ❓ Algemene vragen
    """)
    
    # Toon voorbeeld tracking codes
    if st.checkbox("Toon voorbeeld tracking codes"):
        try:
            df = pd.read_csv('tracking_codes.csv', sep='\t')
            st.dataframe(df[['TrackTraceCode', 'Vervoerder', 'Status']].head(10))
        except:
            st.info("Tracking database geladen")
    
    # Statistieken
    st.divider()
    st.subheader("📈 Chat statistieken")
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    st.metric("Berichten vandaag", st.session_state.message_count)

# Main content
st.title("🤖 Billie - Je Klantenservice Assistent")
st.caption("Altijd hier om je te helpen met je vragen!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Voeg welkomstbericht toe
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hallo! Ik ben Billie. Hoe kan ik je helpen vandaag? Je kunt me vragen stellen over je pakket, retourneren, betalingen of iets anders!"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Typ je vraag hier..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get chatbot response
    with st.chat_message("assistant"):
        with st.spinner("Billie denkt na..."):
            response = chatbot.get_antwoord(prompt)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Extra functionaliteit onder de chat
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 Pakketstatus", use_container_width=True):
        st.info("Voor pakketstatus: geef je Track & Trace code op. Bijvoorbeeld: 'Waar is mijn pakket met code 3SAB123456789NL?'")

with col2:
    if st.button("🔄 Retourneren", use_container_width=True):
        st.info("Retourneren kan binnen 30 dagen. Meld je retour aan via 'Mijn Account' op onze website.")

with col3:
    if st.button("💬 Chatgeschiedenis", use_container_width=True):
        if st.session_state.messages:
            st.subheader("Jouw gesprek")
            for i, msg in enumerate(st.session_state.messages):
                if i > 0:  # Skip welcome message
                    prefix = "👤" if msg["role"] == "user" else "🤖"
                    st.write(f"{prefix} {msg['content'][:100]}...")
        else:
            st.info("Nog geen chatgeschiedenis")

# Voeg een .env template toe in je project
st.sidebar.divider()
st.sidebar.subheader("🔧 Configuratie")
if st.sidebar.button("Toon .env template"):
    st.sidebar.code("""
# .env bestand
GEMINI_API_KEY=je_api_key_hier
MODEL_VERSIE=gemini-pro
""")
