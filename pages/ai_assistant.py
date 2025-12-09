import streamlit as st
import google.generativeai as genai
from arg_database.data_loader import (
    load_cyber_incidents, load_datasets_metadata, load_it_tickets
)


GEMINI_API_KEY = "AIzaSyAvA1-igsmdbSLfqV4JGQCQDYGmXva3wSY"


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

# Create sidebar with navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
st.sidebar.markdown("---")

st.sidebar.page_link("pages/dash.py", label="Dashboard", icon="🏠")

st.sidebar.markdown("---")

# Logout button
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Main page content
st.title("AI Assistant")
st.markdown("### Ask questions about your data")
st.markdown("---")

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