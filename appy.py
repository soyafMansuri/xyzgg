import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from datetime import datetime
import json
import pandas as pd

# Configure the API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Set page title and icon
st.set_page_config(page_title="Healer AI", page_icon="🌼", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "toggle_button" not in st.session_state:
    st.session_state.toggle_button = "Speak"  # Initial state for button
if "mood_tracking" not in st.session_state:
    st.session_state.mood_tracking = []
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

# Custom CSS for improved UI styling
st.markdown("""
    <style>
    body {
        background-color: #f0f4f8;
    }
    .stApp {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-bubble {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        color: white;
    }
    .user-bubble {
        background-color: #3182ce;
        text-align: right;
    }
    .assistant-bubble {
        background-color: #4caf50;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to save chat history
def save_chat():
    if st.session_state.messages:
        chat_summary = st.session_state.messages[0]["content"][:50] + "..."
        current_chat = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "summary": chat_summary,
            "messages": st.session_state.messages.copy()
        }
        st.session_state.chat_history.append(current_chat)
        st.session_state.messages = []
        st.success("Chat saved!")

# Speech-to-Text Function
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak into your microphone.")
        try:
            audio = recognizer.listen(source, timeout=5)
            recognized_text = recognizer.recognize_google(audio)
            st.success("Speech recognized!")
            return recognized_text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand the audio.")
        except sr.RequestError:
            st.error("Error with the speech recognition service.")
    return ""

# Chat Rendering
def render_chat():
    chat_container = st.empty()
    with chat_container.container():
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-bubble user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble assistant-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# Main Container
with st.container():
    st.title("🌼 Healer AI")
    st.markdown(".")

    # Chat Input and Display
    user_input_col1, user_input_col2 = st.columns([5, 1])
    with user_input_col1:
        user_input = st.text_input("Type your message here...")
    with user_input_col2:
        if st.session_state.toggle_button == "Speak":
            if st.button("🎙️ Speak"):
                spoken_text = speech_to_text()
                if spoken_text:
                    user_input = spoken_text
                    st.session_state.toggle_button = "Send"  # Toggle to Send button
        elif st.session_state.toggle_button == "Send":
            if st.button("📤 Send"):
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.toggle_button = "Speak"  # Toggle back to Speak button

    # Process user input and generate response
    if user_input:
        try:
            model_option = "gemini-1.5-flash"  # Default model
            temperature = 0.7  # Default response style

            model = genai.GenerativeModel(
                model_option,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            context = """MediBot is an AI-driven healthcare assistant designed to perform diagnostic, predictive, descriptive, and prescriptive analyses of patient health. Leveraging LLMs, LangChain, and Ollama, it provides real-time assistance by analyzing symptoms, predicting risks, offering diagnoses, and suggesting personalized treatments. MediBot aims to enhance healthcare accessibility, improve diagnostic accuracy, and reduce response times, making quality healthcare available anytime, anywhere."""
            enhanced_prompt = f"{context}\n\nUser: {user_input}"
            response = model.generate_content(enhanced_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Render chat
    render_chat()

# Sidebar Section
with st.sidebar:
    st.header("Wellness Tools")

    # Mood Tracking
    st.subheader("Daily Mood")
    mood = st.select_slider(
        "How are you feeling today?",
        options=["😞", "😕", "😐", "🙂", "😄"],
        value="😐"
    )
    if st.button("Save Mood"):
        st.session_state.mood_tracking.append({"date": datetime.now().strftime("%Y-%m-%d"), "mood": mood})
        st.success("Mood logged!")

    # Journal Entry
    st.subheader("Quick Journal")
    journal_entry = st.text_area("Write your thoughts...", height=100)
    if st.button("Save Journal"):
        if journal_entry:
            st.session_state.journal_entries.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "entry": journal_entry})
            st.success("Journal entry saved!")

    # Export Chat History
    st.subheader("Export Chat History")
    if st.button("Export History"):
        chat_history_df = pd.DataFrame([
            {'date': chat['date'], 'summary': chat['summary'], 'messages': json.dumps(chat['messages'])}
            for chat in st.session_state.chat_history
        ])
        st.download_button(
            label="Download Chat History",
            data=chat_history_df.to_csv(index=False),
            file_name="chat_history.csv",
            mime="text/csv"
        )
