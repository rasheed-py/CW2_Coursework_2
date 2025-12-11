import streamlit as st
import plotly.express as px
from pathlib import Path
import base64
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_cyber_incidents, create_incident, update_incident, delete_incident
)

# Set up the page configuration
st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Check if the user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
if st.session_state.role not in ["user", "cybersecurity"]:
    st.error("Access Denied - You don't have permission to view this page")
    st.stop()

image_path = "imgs/matte.jpg"

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
    st.sidebar.page_link("pages/data_science.py", label="Data Science")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Load incident data from database
df = load_cyber_incidents()

# Main page title
st.title("Cybersecurity Dashboard")
st.markdown("### Incident Response & Threat Analysis")

# Display key metrics in a 2x2 grid
st.markdown("#### System Overview")
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.metric("Total Incidents", len(df))
with row1_col2:
    st.metric("Open Cases", len(df[df['status'] == 'Open']))

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.metric("Critical", len(df[df['severity'] == 'Critical']))
with row2_col2:
    st.metric("Phishing Alerts", len(df[df['category'] == 'Phishing']))

st.markdown("---")

# Create tabs - only Incidents and Analysis
tab1, tab2 = st.tabs(["Incidents Management", "Threat Analysis"])

# Tab 1: Incident Management
with tab1:
    # Create new incident form (always visible)
    st.markdown("#### Create New Incident")
    with st.form("create_incident"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_id = st.number_input("Incident ID", min_value=1, value=int(df['incident_id'].max() + 1))
            new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        with col2:
            new_timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            new_category = st.selectbox("Category",
                                        ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Misconfiguration"])
        with col3:
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])

        new_description = st.text_area("Description")

        if st.form_submit_button("Create Incident"):
            create_incident(new_id, new_timestamp, new_severity, new_category, new_status, new_description)
            st.success("Incident created successfully")
            st.rerun()

    st.markdown("---")

    # Display all incidents
    st.markdown("#### All Incidents")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Update Incident")
        update_id = st.selectbox("Select Incident ID", df['incident_id'].values)
        incident = df[df['incident_id'] == update_id].iloc[0]

        with st.form("update_incident"):
            upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"],
                                      index=["Open", "In Progress", "Resolved", "Closed"].index(incident['status']))
            upd_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"],
                                        index=["Low", "Medium", "High", "Critical"].index(incident['severity']))

            if st.form_submit_button("Update"):
                update_incident(update_id, status=upd_status, severity=upd_severity)
                st.success("Incident updated successfully")
                st.rerun()

    with col2:
        st.markdown("#### Delete Incident")
        delete_id = st.selectbox("Select Incident ID to Delete", df['incident_id'].values, key="delete")
        st.markdown("")
        st.markdown("")
        if st.button("Delete Incident", type="primary"):
            delete_incident(delete_id)
            st.success("Incident deleted successfully")
            st.rerun()

# Tab 2: Analysis
with tab2:
    # Phishing analysis at the top
    st.markdown("#### High-Value Insight: Phishing Surge Analysis")
    phishing_df = df[df['category'] == 'Phishing']

    analysis_col1, analysis_col2 = st.columns([1, 2])

    with analysis_col1:
        st.metric("Total Phishing Incidents", len(phishing_df))
        st.metric("Unresolved Phishing", len(phishing_df[phishing_df['status'].isin(['Open', 'In Progress'])]))

    with analysis_col2:
        phish_status = phishing_df['status'].value_counts()
        fig = px.pie(values=phish_status.values, names=phish_status.index,
                     title="Phishing Incident Status")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Charts section
    st.markdown("#### Incident Statistics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        category_counts = df['category'].value_counts()
        fig1 = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            labels={'x': 'Category', 'y': 'Count'},
            title="Incidents by Category"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        severity_counts = df['severity'].value_counts()
        fig2 = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Severity Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Resolution bottleneck
    st.markdown("#### Resolution Bottleneck Analysis")
    status_summary = df.groupby(['category', 'status']).size().reset_index(name='count')
    fig = px.bar(status_summary, x='category', y='count', color='status',
                 title="Incidents by Category and Status",
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Key Finding: Phishing incidents show the longest resolution times, with the highest concentration in 'In Progress' status, indicating a response bottleneck.")

st.markdown("---")
st.caption("Cybersecurity Module - A.R.G.U.S.")