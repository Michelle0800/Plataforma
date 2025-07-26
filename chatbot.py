# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import os
import uuid
from datetime import datetime
from pathlib import Path
from functools import lru_cache

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
st.set_page_config(
    page_title="Michelle Souza",
    page_icon="💋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Meta tag para viewport mobile
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-top: 0rem;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    header {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ajustes para mobile */
    @media screen and (max-width: 768px) {
        [data-testid="stVerticalBlock"] {
            gap: 0.2rem !important;
        }
        .stChatInput {
            bottom: 0;
            position: fixed;
            width: calc(100% - 2rem) !important;
            left: 0;
            padding: 0 1rem;
            background: rgba(0,0,0,0.8) !important;
            z-index: 999;
        }
        .stChatMessage {
            max-width: 80% !important;
        }
        /* Esconder sidebar em mobile */
        section[data-testid="stSidebar"] {
            display: none !important;
            transition: all 0.3s;
        }
        /* Botão para mostrar sidebar */
        .sidebar-toggle {
            position: fixed;
            bottom: 60px;
            right: 10px;
            z-index: 1000;
            background: #ff66b3;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .chat-container {
            padding-bottom: 80px;
        }
        .call-effect {
            max-width: 100% !important;
            margin: 20px 0 !important;
            padding: 20px !important;
        }
    }
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# [...] (Restante das constantes e configurações permanecem iguais)

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
            border-right: 1px solid #ff66b3 !important;
        }
        .stButton button {
            background: rgba(255, 20, 147, 0.2) !important;
            color: white !important;
            border: 1px solid #ff66b3 !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            background: rgba(255, 20, 147, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        [data-testid="stChatInput"] {
            background: rgba(255, 102, 179, 0.1) !important;
            border: 1px solid #ff66b3 !important;
        }
        div.stButton > button:first-child {
            background: linear-gradient(45deg, #ff1493, #9400d3) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            transition: all 0.3s !important;
            box-shadow: 0 4px 8px rgba(255, 20, 147, 0.3) !important;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(255, 20, 147, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    
    ChatService.initialize_session(conn)
    
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.stop()
    
    # Mostrar tela de chamada direto após verificação
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        st.session_state.chat_started = True
        st.session_state.current_page = "chat"
        save_persistent_data()
        
        # Adiciona o botão de menu toggle
        st.markdown("""
        <div class="sidebar-toggle" onclick="toggleSidebar()">☰</div>
        <script>
            function toggleSidebar() {
                const sidebar = parent.document.querySelector('section[data-testid="stSidebar"]');
                if (sidebar.style.display === 'none' || !sidebar.style.display) {
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.transform = 'translateX(0)';
                } else {
                    sidebar.style.display = 'none';
                }
            }
        </script>
        """, unsafe_allow_html=True)
        
        st.rerun()
    
    # Mostrar sidebar após a chamada
    UiService.setup_sidebar()
    
    if st.session_state.current_page == "home":
        NewPages.show_home_page()
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    elif st.session_state.current_page == "offers":
        NewPages.show_offers_page()
    elif st.session_state.current_page == "vip":
        st.session_state.show_vip_offer = True
        save_persistent_data()
        st.rerun()
    elif st.session_state.get("show_vip_offer", False):
        st.warning("Página VIP em desenvolvimento")
        if st.button("Voltar ao chat"):
            st.session_state.show_vip_offer = False
            save_persistent_data()
            st.rerun()
    else:
        UiService.enhanced_chat_ui(conn)
    
    save_persistent_data()

if __name__ == "__main__":
    main()
