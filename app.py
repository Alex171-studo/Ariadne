import streamlit as st
from rag_engine import RAGEngine
from mcp_client import FileSystemMCP
from agent import app as agent_app

st.set_page_config(
    page_title="Ariadne - Dev Assistant",
    page_icon="🧶",
    layout="wide"
)

st.title("🧶 Ariadne — Assistant Développeur")
st.caption("Aide à l'onboarding : explore la doc (RAG) et les fichiers du projet (MCP).")

if "rag_engine" not in st.session_state:
    with st.spinner("Initialisation du moteur RAG..."):
        st.session_state.rag_engine = RAGEngine()

if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = FileSystemMCP()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("⚙️ État du Système")
    st.success("Moteur RAG : Connecté")
    st.success("Client MCP : Prêt")
    st.divider()
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "source" in msg and msg["source"]:
            st.caption(msg["source"])
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose une question sur le projet ou demande un fichier..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ariadne réfléchit et consulte le projet..."):
            config = {
                "configurable": {
                    "rag_instance": st.session_state.rag_engine,
                    "mcp_instance": st.session_state.mcp_client,
                }
            }
            
            final_state = agent_app.invoke(
                {"question": prompt}, 
                config=config
            )
            
            response_text = final_state.get("response", "Une erreur est survenue.")
            source_used = final_state.get("source_used")
            st.caption(source_used)
            st.markdown(response_text)
            
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "source": source_used,
    })