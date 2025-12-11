import streamlit as st
import google.generativeai as genai
from arg_database.data_loader import (
    load_cyber_incidents, load_datasets_metadata, load_it_tickets
)
from pathlib import Path
import base64

import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from dotenv import load_dotenv

load_dotenv()

# Set up the page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Check if the user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()


image_path = "imgs/blue.jpg"

# Check if image exists and apply background
if Path(image_path).exists():
    # Read the image as bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Determine MIME type
    if image_path.lower().endswith(('.png')):
        mime = "image/png"
    elif image_path.lower().endswith(('.jpg', '.jpeg')):
        mime = "image/jpeg"
    elif image_path.lower().endswith(('.gif')):
        mime = "image/gif"
    else:
        mime = "image/jpeg"

    encoded = base64.b64encode(image_bytes).decode()

    # Inject CSS with the image
    st.markdown(
        f"""
        <style>
        /* Target the main app container */
        .stApp {{
           background-image: url("data:{mime};base64,{encoded}");
            background-size: cover;  /* Options: cover, contain, 100% 100%, auto */
            background-position: center center;  /* Options: top, bottom, left, right, center */
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Make content readable */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {{
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 10px;
        }}

        header {{
            background: transparent !important;
        }}

        [data-testid="stToolbar"] {{
            display: none;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown(""" 
<style>
.stButton > button {
    border: 2px solid #DC143C;
}

.stButton > button:hover {
    background-color: #DC143C;
    color: white;
    border: 2px solid #DC143C;
}
</style>
""", unsafe_allow_html=True)

# Create sidebar with navigation
st.sidebar.title("ARG NAVIGATION💢")
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")

# Add navigation links
st.sidebar.page_link("pages/dash.py", label="Dashboard")
if st.session_state.role == "user":
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/data_science.py", label="Data Science")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations")

st.sidebar.markdown("---")

# Logout button
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Main page content
st.title("AI ASSISTANT \" GIDEON \" 🗣️")
st.markdown("### Ask questions about ARGUS data")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Function to load all data and create context
def get_data_context():
    """Load all domain data and create a summary for the AI"""
    context = "Here is the current data from the platform:\n\n"

    # Load cybersecurity data
    cyber_df = load_cyber_incidents()
    context += f"CYBERSECURITY:\n"
    context += f"- Total incidents: {len(cyber_df)}\n"
    context += f"- Open incidents: {len(cyber_df[cyber_df['status'] == 'Open'])}\n"
    context += f"- Critical incidents: {len(cyber_df[cyber_df['severity'] == 'Critical'])}\n"
    context += f"- Phishing incidents: {len(cyber_df[cyber_df['category'] == 'Phishing'])}\n\n"

    # Load data science data
    datasets_df = load_datasets_metadata()
    context += f"DATASETS:\n"
    context += f"- Total datasets: {len(datasets_df)}\n"
    context += f"- Total rows: {datasets_df['rows'].sum()}\n\n"

    # Load IT operations data
    tickets_df = load_it_tickets()
    context += f"IT TICKETS:\n"
    context += f"- Total tickets: {len(tickets_df)}\n"
    context += f"- Open tickets: {len(tickets_df[tickets_df['status'] == 'Open'])}\n"
    context += f"- Average resolution time: {tickets_df['resolution_time_hours'].mean():.1f} hours\n"

    return context


# Function to get AI response
def get_ai_response(user_message):
    """Send message to Gemini AI and get response"""
    try:
        # Configure the API with your key
        genai.configure(api_key=GEMINI_API_KEY)

        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Get current data context
        data_context = get_data_context()

        # Create the full prompt with context
        full_prompt = f"""{data_context}

User question: {user_message}

Please provide a helpful response based on the data above."""

        # Generate response
        response = model.generate_content(full_prompt)

        return response.text

    except Exception as e:
        return f"Error: {str(e)}"


# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# Chat input
user_input = st.chat_input("Ask me anything about your data...")

# Process user input
if user_input:
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_response = get_ai_response(user_input)
            st.write(ai_response)

    # Add AI response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": ai_response
    })

    # Rerun to update the display
    st.rerun()

# Clear chat button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("---")
st.caption("AI Assistant - A.R.G.U.S.")