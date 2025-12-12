import streamlit as st
from pathlib import Path
import base64

# Configure the Streamlit page settings
st.set_page_config(
    page_title="A.R.G.U.S. Dashboard",
    page_icon="🅰️",
    layout="wide"
)

# Check if user is logged in - redirect to login if not
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error(" Please login first")
    st.stop()

# Path to background image
image_path = "imgs/matte.jpg"

# Apply background image styling if the file exists
if Path(image_path).exists():
    # Read the image file as bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Determine MIME type based on file extension
    if image_path.lower().endswith(('.png')):
        mime = "image/png"
    elif image_path.lower().endswith(('.jpg', '.jpeg')):
        mime = "image/jpeg"
    elif image_path.lower().endswith(('.gif')):
        mime = "image/gif"
    else:
        mime = "image/jpeg"

    # Encode image to base64 for embedding in CSS
    encoded = base64.b64encode(image_bytes).decode()

    # Inject custom CSS with background image
    st.markdown(
        f"""
        <style>
        /* Background on whole app */
        .stApp {{
            background-image: url("data:{mime};base64,{encoded}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Main content readable */
        .main .block-container {{
            background: rgba(255, 255, 255, 0.9) !important;
            padding: 2rem !important;
            border-radius: 10px !important;
        }}

        /* Don't mess with sidebar at all - let it be default */

        </style>
        """,
        unsafe_allow_html=True
    )

# Add custom button styling
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
st.sidebar.write(f" User: {st.session_state.username}")
st.sidebar.write(f" Role: {st.session_state.role}")

# Display navigation links based on user role
if st.session_state.role == "user":
    # User role has access to all modules
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/data_science.py", label="Data Science")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")
elif st.session_state.role == "cybersecurity":
    # Cybersecurity role - only cybersecurity module
    st.sidebar.page_link("pages/cybersecurity.py", label=" Cybersecurity Dashboard")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")
elif st.session_state.role == "data_scientist":
    # Data scientist role - only data science module
    st.sidebar.page_link("pages/data_science.py", label="Data Science Dashboard")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")
elif st.session_state.role == "it_admin":
    # IT admin role - only IT operations module
    st.sidebar.page_link("pages/IT_tickets.py", label=" IT Operations Dashboard")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")

st.sidebar.markdown("---")

# Logout button - clears session state and returns to login
if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Main content - welcome message
st.title(f"WELCOME... {st.session_state.username}! ")
st.markdown("---")

# Display role-specific dashboard based on user's role
if st.session_state.role == "user":
    # User role - show all available modules
    st.subheader("AUTHORIZED User Dashboard")
    st.info("You have full access to all domains")

    st.markdown("---")

    # Top row - 2 columns for Cybersecurity and Data Science
    top_col1, top_col2 = st.columns(2)

    with top_col1:
        st.markdown("### Cybersecurity")
        st.write("Monitor security incidents and threats")
        if st.button("Go to Cybersecurity", use_container_width=True, key="cyber"):
            st.switch_page("pages/cybersecurity.py")

    with top_col2:
        st.markdown("### Data Science")
        st.write("Manage and analyze datasets")
        if st.button("Go to Data Science", use_container_width=True, key="data"):
            st.switch_page("pages/data_science.py")

    st.markdown("---")

    # Bottom row - 1 centered column for IT Operations
    bottom_left, bottom_center, bottom_right = st.columns([1, 2, 1])

    with bottom_center:
        st.markdown("###  IT Operations")
        st.write("Track IT tickets and performance")
        if st.button("Go to IT Operations", use_container_width=True, key="it"):
            st.switch_page("pages/IT_tickets.py")

elif st.session_state.role == "cybersecurity":
    # Cybersecurity analyst dashboard
    st.subheader(" Cybersecurity Analyst")
    st.info("Access to incident management and threat analysis")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/cybersecurity.py")

elif st.session_state.role == "data_scientist":
    # Data scientist dashboard
    st.subheader("Data Scientist")
    st.info("Access to dataset management and analytics")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/data_science.py")

elif st.session_state.role == "it_admin":
    # IT administrator dashboard
    st.subheader("IT Administrator")
    st.info("Access to ticket management and performance monitoring")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/IT_tickets.py")

st.markdown("---")
st.caption("A.R.G.U.S. - Advanced Research Group United Support")