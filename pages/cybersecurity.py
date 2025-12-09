import streamlit as st
import plotly.express as px
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
# If not logged in, show error and stop the page from loading
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
# Only 'user' and 'cybersecurity' roles can access this dashboard
if st.session_state.role not in ["user", "cybersecurity"]:
    st.error("Access Denied - You don't have permission to view this page")
    st.stop()

# Create sidebar with navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")
st.sidebar.markdown("---")

# Add navigation links
st.sidebar.page_link("pages/dash.py", label="Dashboard", icon="🏠")
if st.session_state.role == "user":
    st.sidebar.page_link("pages/data_science.py", label="Data Science", icon="📊")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations", icon="💻")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load incident data from database
df = load_cyber_incidents()

# Main page title and description
st.title("Cybersecurity Dashboard")
st.markdown("### Incident Response & Threat Analysis")
st.markdown("---")

# Display key metrics at the top of the page
# Split into 4 columns for better layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Count total incidents
    st.metric("Total Incidents", len(df))
with col2:
    # Count incidents with 'Open' status
    open_cases = len(df[df['status'] == 'Open'])
    st.metric("Open Cases", open_cases)
with col3:
    # Count critical severity incidents
    critical = len(df[df['severity'] == 'Critical'])
    st.metric("Critical", critical)
with col4:
    # Count phishing category incidents
    phishing = len(df[df['category'] == 'Phishing'])
    st.metric("Phishing Alerts", phishing)

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Overview", "Incidents", "Analysis"])

# Tab 1: Overview with charts and visualizations
with tab1:
    st.subheader("Threat Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Create bar chart showing incidents by category
        st.markdown("#### Incidents by Category")
        category_counts = df['category'].value_counts()
        fig1 = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            labels={'x': 'Category', 'y': 'Count'},
            title="Incident Categories"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Create pie chart showing severity distribution
        st.markdown("#### Severity Distribution")
        severity_counts = df['severity'].value_counts()
        fig2 = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Severity Levels"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Bar chart showing incident status
    st.markdown("#### Incident Status")
    status_counts = df['status'].value_counts()
    fig3 = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        labels={'x': 'Status', 'y': 'Count'},
        color=status_counts.index
    )
    st.plotly_chart(fig3, use_container_width=True)

# Tab 2: Incident Management (CRUD operations)
with tab2:
    st.subheader("Incident Management")

    # Create new incident form (always visible, no dropdown)
    st.markdown("#### Create New Incident")
    with st.form("create_incident"):
        # Generate next available incident ID
        new_id = st.number_input("Incident ID", min_value=1, value=int(df['incident_id'].max() + 1))
        # Get current timestamp for the incident
        new_timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Dropdown for severity level
        new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        # Dropdown for incident category
        new_category = st.selectbox("Category",
                                    ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Misconfiguration"])
        # Dropdown for incident status
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        # Text area for incident description
        new_description = st.text_area("Description")

        # Submit button for the form
        if st.form_submit_button("Create Incident"):
            # Call function to create incident in database
            create_incident(new_id, new_timestamp, new_severity, new_category, new_status, new_description)
            st.success("Incident created successfully")
            # Refresh the page to show new data
            st.rerun()

    st.markdown("---")

    # Display all incidents in a table (no filters)
    st.markdown("#### All Incidents")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections side by side
    col1, col2 = st.columns(2)

    with col1:
        # Update incident section
        with st.expander("Update Incident"):
            # Dropdown to select which incident to update
            update_id = st.selectbox("Select Incident ID", df['incident_id'].values)
            # Get the selected incident data
            incident = df[df['incident_id'] == update_id].iloc[0]

            with st.form("update_incident"):
                # Dropdown for new status with current value pre-selected
                upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"],
                                          index=["Open", "In Progress", "Resolved", "Closed"].index(incident['status']))
                # Dropdown for new severity with current value pre-selected
                upd_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"],
                                            index=["Low", "Medium", "High", "Critical"].index(incident['severity']))

                # Submit button to update
                if st.form_submit_button("Update"):
                    # Call function to update incident in database
                    update_incident(update_id, status=upd_status, severity=upd_severity)
                    st.success("Incident updated successfully")
                    st.rerun()

    with col2:
        # Delete incident section
        with st.expander("Delete Incident"):
            # Dropdown to select which incident to delete
            delete_id = st.selectbox("Select Incident ID to Delete", df['incident_id'].values, key="delete")

            # Delete button with warning styling
            if st.button("Delete Incident", type="primary"):
                # Call function to delete incident from database
                delete_incident(delete_id)
                st.success("Incident deleted successfully")
                st.rerun()

# Tab 3: Analysis and insights
with tab3:
    st.subheader("Threat Analysis")

    # High-value insight section for phishing analysis
    st.markdown("#### High-Value Insight: Phishing Surge Analysis")
    # Filter data to only show phishing incidents
    phishing_df = df[df['category'] == 'Phishing']

    col1, col2 = st.columns(2)

    with col1:
        # Display metrics for phishing incidents
        st.metric("Total Phishing Incidents", len(phishing_df))
        # Count unresolved phishing (Open or In Progress)
        st.metric("Unresolved Phishing", len(phishing_df[phishing_df['status'].isin(['Open', 'In Progress'])]))

    with col2:
        # Pie chart showing status breakdown for phishing
        phish_status = phishing_df['status'].value_counts()
        fig = px.pie(values=phish_status.values, names=phish_status.index,
                     title="Phishing Incident Status")
        st.plotly_chart(fig, use_container_width=True)

    # Resolution bottleneck analysis
    st.markdown("#### Resolution Bottleneck Analysis")
    # Group data by category and status
    status_summary = df.groupby(['category', 'status']).size().reset_index(name='count')
    # Create grouped bar chart
    fig = px.bar(status_summary, x='category', y='count', color='status',
                 title="Incidents by Category and Status",
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # Display key finding
    st.info(
        "Key Finding: Phishing incidents show the longest resolution times, with the highest concentration in 'In Progress' status, indicating a response bottleneck.")

st.markdown("---")
st.caption("Cybersecurity Module - A.R.G.U.S.")