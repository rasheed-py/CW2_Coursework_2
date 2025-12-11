import streamlit as st

# Page configuration
st.set_page_config(
    page_title="A.R.G.U.S. Dashboard",
    page_icon="🅰️",
    layout="wide"
)

# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error(" Please login first")
    st.stop()

# Sidebar navigation
st.sidebar.title("ARG NAVIGATION💢")
st.sidebar.write(f" User: {st.session_state.username}")
st.sidebar.write(f" Role: {st.session_state.role}")

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

# Navigation links based on role
if st.session_state.role == "user":
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/data_science.py", label="Data Science")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations")
elif st.session_state.role == "cybersecurity":
    st.sidebar.page_link("pages/cybersecurity.py", label=" Cybersecurity Dashboard")
elif st.session_state.role == "data_scientist":
    st.sidebar.page_link("pages/data_science.py", label="Data Science Dashboard")
elif st.session_state.role == "it_admin":
    st.sidebar.page_link("pages/IT_tickets.py", label=" IT Operations Dashboard")

st.sidebar.markdown("---")

# Logout button
if st.sidebar.button(" Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Main content
st.title(f"WELCOME... {st.session_state.username}! ")
st.markdown("---")

# Role-specific welcome - 2 TOP, 1 BOTTOM CENTERED
if st.session_state.role == "user":
    st.subheader("AUTHORIZED User Dashboard")
    st.info("You have full access to all domains")

    st.markdown("---")

    # Top row - 2 columns
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

    # Bottom row - 1 centered column
    bottom_left, bottom_center, bottom_right = st.columns([1, 2, 1])

    with bottom_center:
        st.markdown("###  IT Operations")
        st.write("Track IT tickets and performance")
        if st.button("Go to IT Operations", use_container_width=True, key="it"):
            st.switch_page("pages/IT_tickets.py")

elif st.session_state.role == "cybersecurity":
    st.subheader(" Cybersecurity Analyst")
    st.info("Access to incident management and threat analysis")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/cybersecurity.py")

elif st.session_state.role == "data_scientist":
    st.subheader("Data Scientist")
    st.info("Access to dataset management and analytics")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/data_science.py")

elif st.session_state.role == "it_admin":
    st.subheader("IT Administrator")
    st.info("Access to ticket management and performance monitoring")
    if st.button("Go to Your Dashboard", use_container_width=True):
        st.switch_page("pages/IT_tickets.py")

st.markdown("---")
st.caption("A.R.G.U.S. - Advanced Research Group United Support")