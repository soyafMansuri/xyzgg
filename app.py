import streamlit as st
from datetime import datetime
import json
import pandas as pd

from google.cloud import translate_v2 as translate

import google.generativeai as genai 

def translate_text(text, target_language):
    # Initialize the client
    client = translate.Client()
# Configure the API key


# Set page title and icon
st.set_page_config(page_title="Healer", page_icon="🤖", layout="wide")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mood_tracking" not in st.session_state:
    st.session_state.mood_tracking = []
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f7f9;
    }
    .main-content {
        padding: 1rem;
    }
    .chat-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        min-height: 400px;
    }
    .emergency-button {
        background-color: #ff4b4b;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    .history-item {
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to save current chat
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
        st.success("Chat saved to history!")

# Function to load chat from history
def load_chat(chat_id):
    for chat in st.session_state.chat_history:
        if chat["id"] == chat_id:
            st.session_state.messages = chat["messages"].copy()
            st.session_state.selected_chat = chat_id
            st.rerun()

# Main container
with st.container():
    st.title("🌟 Welcome To Healer")
    st.markdown("Your AI companion for mental wellness and support")

    # Create main layout
    chat_col, sidebar_col = st.columns([3, 1])

    with chat_col:
        # Chat controls
        chat_controls_col1, chat_controls_col2 = st.columns([2, 1])
        with chat_controls_col1:
            st.markdown("### Chat with Healer")
        with chat_controls_col2:
            if st.button("Save Current Chat", key="save_chat"):
                save_chat()
        
        # Chat container
        with st.container():
            chat_container = st.empty()
            with chat_container.container():
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # Chat input
            user_input = st.chat_input("Chat with Healer...")

    with sidebar_col:
        # Wellness Tools Section
        st.markdown("### Wellness Tools")
        
        # Mood Tracking
        st.subheader("Daily Mood")
        mood = st.select_slider(
            "How are you feeling today?",
            options=["😞", "😕", "😐", "🙂", "😄"],
            value="😐"
        )
        if st.button("Save Mood"):
            st.session_state.mood_tracking.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mood": mood
            })
            st.success("Mood logged!")

        # Journal Entry
        st.markdown("### Quick Journal")
        journal_entry = st.text_area("Write your thoughts...", height=100)
        if st.button("Save Journal"):
            if journal_entry:
                st.session_state.journal_entries.append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "entry": journal_entry
                })
                st.success("Saved!")

# Sidebar configuration
with st.sidebar:
    # Model Configuration
    st.header("Settings & Resources")
    with st.expander("Chat Settings"):
        model_option = st.selectbox(
            "Choose Gemini Model",
            ["gemini-1.5-flash", "gemini-1.5-pro"]
        )
        
        temperature = st.slider(
            "Response Style",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values: more creative, Lower values: more focused"
        )

    # Chat History Section
    st.markdown("---")
    st.header("Chat History")
    if st.session_state.chat_history:
        for chat in reversed(st.session_state.chat_history):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        f"{chat['date']}\n{chat['summary']}", 
                        key=f"chat_{chat['id']}",
                        help="Click to load this chat"
                    ):
                        load_chat(chat['id'])
                with col2:
                    if st.button("🗑️", key=f"delete_{chat['id']}", help="Delete chat"):
                        st.session_state.chat_history.remove(chat)
                        if st.session_state.selected_chat == chat['id']:
                            st.session_state.messages = []
                        st.rerun()
    else:
        st.info("No chat history yet. Your saved chats will appear here.")

    # Emergency Resources
    st.markdown("---")
    st.header("Emergency Resources")
    st.markdown("""
    🆘 **Emergency Helplines:**
    - National Crisis Helpline: 988
    - Emergency Services: 911
    """)
    
    if st.button("Click for Immediate Help", type="primary"):
        st.markdown("""
        ### Crisis Resources:
        1. Call 988 for immediate support
        2. Text HOME to 741741
        3. Contact your local emergency room
        """)

    # Therapist Directory
    st.markdown("---")
    st.header("Find a Therapist")
    with st.expander("View Therapist Directory"):
        therapists = [
            {"name": "Dr. Amit Sharma", "location": "New Delhi, Delhi"},
            {"name": "Dr. Ajit Dandekar", "location": "Raghunath Nagar, Bhopal"},
            {"name": "Dr. Mimansa Singh Tanwar", "location": "Indore"},
            {"name": "Dr. Shraboni Nandi", "location": "New Delhi, Delhi"},
            {"name": "Dr. G B Singh", "location": "Delhi"},
            {"name": "Dr. Murali Raj", "location": "Shivaji Market, Pune"},
            {"name": "Dr. Vipul Rastogi", "location": "Shri Ram Colony, Bhopal"},
            {"name": "Dr. Karuna Singh", "location": "Udaipur"},
            {"name": "Dr. Dipti Yadav", "location": "Nilami Society, Ahmedabad"},
            {"name": "Dr. Kratu Sharma", "location": "Gandhinagar Highway, Ahmedabad"}
        ]
        for therapist in therapists:
            st.markdown(f"""
            **{therapist['name']}**  
            {therapist['location']}
            ---
            """)

    # Export Options
    st.markdown("---")
    st.header("Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export History"):
            chat_history_df = pd.DataFrame([{
                'date': chat['date'],
                'summary': chat['summary'],
                'messages': json.dumps(chat['messages'])
            } for chat in st.session_state.chat_history])
            st.download_button(
                label="Download CSV",
                data=chat_history_df.to_csv(index=False),
                file_name="chat_history.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export Journal"):
            df_journal = pd.DataFrame(st.session_state.journal_entries)
            st.download_button(
                label="Download CSV",
                data=df_journal.to_csv(index=False),
                file_name="journal_entries.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Export Mood Log"):
            df_mood = pd.DataFrame(st.session_state.mood_tracking)
            st.download_button(
                label="Download CSV",
                data=df_mood.to_csv(index=False),
                file_name="mood_history.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.info("Powered by Gemini")

# Process user input for chat
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        # Create model with selected configuration
        model = genai.GenerativeModel(
            model_option,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        
        # Add context to the prompt
        context = """You are Soyaf,a chatbot which is designed in a way in which you can help different patient and patient in emergency like situation. 
        patients will ask you about thier disease by most of the time telling symptomps, previous health trend etc. process it amd then 
        Provide response which  while maintaining appropriate boundaries. 
        If users express serious concerns, guide them to professional help."""
        
        enhanced_prompt = f"{context}\n\nUser: {user_input}"
        
        # Generate response
        response = model.generate_content(enhanced_prompt)
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        # Rerun to update chat display
        st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {e}")