cat > app.py << 'EOF'
import os
import time
import textwrap
import streamlit as st
import google.generativeai as genai

# --- Page Config (Must be first) ---
st.set_page_config(
    page_title="Pulsage Mission Control",
    layout="wide",
)

# --- Constants ---
GEMINI_MODEL_NAME = "gemini-2.0-flash"
DEFAULT_SYSTEM_PROMPT = """
You are a space-themed AI assistant embedded in a futuristic mission control interface.
Your role: Be concise, clear, helpful. Use a subtle sci-fi tone.
"""

# --- Styling ---
st.markdown(
    """
    <style>
        body { background-color: #020617; color: #e2e8f0; }
        .stApp { background: radial-gradient(ellipse at top, #020617 0%, #000000 100%); }
        .pulse-title { text-align: center; color: #38bdf8; font-size: 3rem; font-weight: 700; }
        .pulse-subtitle { text-align: center; color: #94a3b8; margin-top: -0.5rem; margin-bottom: 2rem; }
        .status-box { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); padding: 1rem; border-radius: 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Helper Functions ---
def get_api_key():
    # Try different env var names just in case
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

class GeminiChatModel:
    def __init__(self):
        api_key = get_api_key()
        if not api_key:
            self.model = None
            st.sidebar.error("❌ GEMINI_API_KEY not found.")
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        except Exception as e:
            self.model = None
            st.sidebar.error(f"❌ Error connecting to AI: {e}")

    def send(self, system_prompt, messages):
        if not self.model:
            return "⚠️ AI System Offline (Check API Key)"
        
        try:
            # Simple history conversion
            history = []
            for msg in messages[:-1]: # All except last
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            chat = self.model.start_chat(history=history)
            prompt = f"{system_prompt}\n\nUser: {messages[-1]['content']}"
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Transmission Error: {str(e)}"

# --- UI Layout ---
st.markdown('<div class="pulse-title">🚀 Pulsage Mission Control</div>', unsafe_allow_html=True)
st.markdown('<div class="pulse-subtitle">Space-themed analytics with a FREE Gemini AI copilot</div>', unsafe_allow_html=True)
st.divider()

# --- Sidebar & Chat ---
st.sidebar.header("🛰 AI Copilot")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Model
if "model" not in st.session_state:
    st.session_state.model = GeminiChatModel()

# Display History
for msg in st.session_state.messages:
    with st.sidebar.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat Input
if prompt := st.sidebar.chat_input("Transmit message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.sidebar.chat_message("user"):
        st.write(prompt)
    
    with st.sidebar.chat_message("assistant"):
        with st.spinner("Receiving signal..."):
            response = st.session_state.model.send(DEFAULT_SYSTEM_PROMPT, st.session_state.messages)
            st.write(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Main Dashboard ---
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="status-box"><h3>🌌 System Status</h3><ul><li>Navigation: Online</li><li>Telemetry: Stable</li><li>AI Model: Gemini 2.0 Flash</li></ul></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="status-box"><h3>🧭 Mission Notes</h3><p>Dashboard active. Ready for launch.</p></div>', unsafe_allow_html=True)

st.divider()
st.info("📡 Telemetry data visualizations will appear here.")
EOF
