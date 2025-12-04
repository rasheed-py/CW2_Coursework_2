import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_cyber_incidents, create_incident, update_incident, delete_incident
)

# Page configuration
st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first")
    st.stop()

# Check role access
if st.session_state.role not in ["user", "cybersecurity"]:
    st.error("🚫 Access Denied - You don't have permission to view this page")
    st.stop()

# Sidebar
st.sidebar.title("🎯 Navigation")
st.sidebar.markdown("---")
st.sidebar.write(f"**👤 User:** {st.session_state.username}")
st.sidebar.write(f"**🎭 Role:** {st.session_state.role}")
st.sidebar.markdown("---")

st.sidebar.page_link("pages/dash.py", label="🏠 Dashboard", icon="🏠")
if st.session_state.role == "user":
    st.sidebar.page_link("pages/data_science.py", label="📊 Data Science", icon="📊")
    st.sidebar.page_link("pages/IT_tickets.py", label="💻 IT Operations", icon="💻")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load data
df = load_cyber_incidents()

# Main content
st.title("🛡️ Cybersecurity Dashboard")
st.markdown("### Incident Response & Threat Analysis")
st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents", len(df))
with col2:
    open_cases = len(df[df['status'] == 'Open'])
    st.metric("Open Cases", open_cases)
with col3:
    critical = len(df[df['severity'] == 'Critical'])
    st.metric("Critical", critical)
with col4:
    phishing = len(df[df['category'] == 'Phishing'])
    st.metric("Phishing Alerts", phishing)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Incidents", "🔍 Analysis"])

with tab1:
    st.subheader("Threat Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Category distribution
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
        # Severity breakdown
        st.markdown("#### Severity Distribution")
        severity_counts = df['severity'].value_counts()
        fig2 = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Severity Levels"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Status distribution
    st.markdown("#### Incident Status")
    status_counts = df['status'].value_counts()
    fig3 = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        labels={'x': 'Status', 'y': 'Count'},
        color=status_counts.index
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Incident Management")

    # Add new incident
    with st.expander("➕ Create New Incident"):
        with st.form("create_incident"):
            new_id = st.number_input("Incident ID", min_value=1, value=int(df['incident_id'].max() + 1))
            new_timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            new_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            new_category = st.selectbox("Category",
                                        ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Misconfiguration"])
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
            new_description = st.text_area("Description")

            if st.form_submit_button("Create Incident"):
                create_incident(new_id, new_timestamp, new_severity, new_category, new_status, new_description)
                st.success("✅ Incident created!")
                st.rerun()

    # View and manage incidents
    st.markdown("#### All Incidents")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.multiselect("Filter by Status", df['status'].unique(), default=df['status'].unique())
    with col2:
        filter_severity = st.multiselect("Filter by Severity", df['severity'].unique(), default=df['severity'].unique())
    with col3:
        filter_category = st.multiselect("Filter by Category", df['category'].unique(), default=df['category'].unique())

    # Apply filters
    filtered_df = df[
        (df['status'].isin(filter_status)) &
        (df['severity'].isin(filter_severity)) &
        (df['category'].isin(filter_category))
        ]

    st.dataframe(filtered_df, use_container_width=True)

    # Update/Delete operations
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("✏️ Update Incident"):
            update_id = st.selectbox("Select Incident ID", df['incident_id'].values)
            incident = df[df['incident_id'] == update_id].iloc[0]

            with st.form("update_incident"):
                upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"],
                                          index=["Open", "In Progress", "Resolved", "Closed"].index(incident['status']))
                upd_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"],
                                            index=["Low", "Medium", "High", "Critical"].index(incident['severity']))

                if st.form_submit_button("Update"):
                    update_incident(update_id, status=upd_status, severity=upd_severity)
                    st.success("✅ Incident updated!")
                    st.rerun()

    with col2:
        with st.expander("🗑️ Delete Incident"):
            delete_id = st.selectbox("Select Incident ID to Delete", df['incident_id'].values, key="delete")

            if st.button("Delete Incident", type="primary"):
                delete_incident(delete_id)
                st.success("✅ Incident deleted!")
                st.rerun()

with tab3:
    st.subheader("Threat Analysis")

    # Phishing spike analysis
    st.markdown("#### 🎯 High-Value Insight: Phishing Surge Analysis")
    phishing_df = df[df['category'] == 'Phishing']

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Phishing Incidents", len(phishing_df))
        st.metric("Unresolved Phishing", len(phishing_df[phishing_df['status'].isin(['Open', 'In Progress'])]))

    with col2:
        # Status breakdown for phishing
        phish_status = phishing_df['status'].value_counts()
        fig = px.pie(values=phish_status.values, names=phish_status.index,
                     title="Phishing Incident Status")
        st.plotly_chart(fig, use_container_width=True)

    # Resolution bottleneck
    st.markdown("#### ⏱️ Resolution Bottleneck Analysis")
    status_summary = df.groupby(['category', 'status']).size().reset_index(name='count')
    fig = px.bar(status_summary, x='category', y='count', color='status',
                 title="Incidents by Category and Status",
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **Key Finding**: Phishing incidents show the longest resolution times, with the highest concentration in 'In Progress' status, indicating a response bottleneck.")

st.markdown("---")
st.caption("🛡️ Cybersecurity Module - A.R.G.U.S.")