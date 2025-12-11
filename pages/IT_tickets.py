import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_it_tickets, create_ticket, update_ticket, delete_ticket
)

# Set up the page configuration
st.set_page_config(
    page_title="IT Operations Dashboard",
    page_icon="💻",
    layout="wide"
)

# Check if the user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
if st.session_state.role not in ["user", "it_admin"]:
    st.error("Access Denied - You don't have permission to view this page")
    st.stop()

# Create sidebar with navigation
st.sidebar.title("ARG NAVIGATION💢")
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")

# Add navigation links
st.sidebar.page_link("pages/dash.py", label="Dashboard")
if st.session_state.role == "user":
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/data_science.py", label="Data Science")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Load ticket data from database
df = load_it_tickets()

# Main page title
st.title("IT Operations Dashboard")
st.markdown("### Service Desk Performance & Ticket Management")

# Display key metrics in a 2x2 grid
st.markdown("#### System Overview")
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.metric("Total Tickets", len(df))
with row1_col2:
    st.metric("Open Tickets", len(df[df['status'] == 'Open']))

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    avg_resolution = df['resolution_time_hours'].mean()
    st.metric("Avg Resolution", f"{avg_resolution:.1f} hrs")
with row2_col2:
    st.metric("Critical", len(df[df['priority'] == 'Critical']))

st.markdown("---")

# Create tabs - only Tickets and Analysis
tab1, tab2 = st.tabs(["Ticket Management", "Performance Analysis"])

# Tab 1: Ticket Management
with tab1:
    # Create new ticket form (always visible)
    st.markdown("#### Create New Ticket")
    with st.form("create_ticket"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_id = st.number_input("Ticket ID", min_value=1, value=int(df['ticket_id'].max() + 1))
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        with col2:
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"])
            new_assigned = st.selectbox("Assign To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
        with col3:
            new_created = st.text_input("Created At", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            new_resolution = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0)

        new_description = st.text_area("Description")

        if st.form_submit_button("Create Ticket"):
            create_ticket(new_id, new_priority, new_description, new_status,
                          new_assigned, new_created, new_resolution)
            st.success("Ticket created successfully")
            st.rerun()

    st.markdown("---")

    # Display all tickets
    st.markdown("#### All Tickets")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Update Ticket")
        update_id = st.selectbox("Select Ticket ID", df['ticket_id'].values)
        ticket = df[df['ticket_id'] == update_id].iloc[0]

        with st.form("update_ticket"):
            upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"],
                                      index=["Open", "In Progress", "Resolved", "Waiting for User"].index(
                                          ticket['status']))
            upd_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"],
                                        index=["Low", "Medium", "High", "Critical"].index(ticket['priority']))
            upd_resolution = st.number_input("Resolution Time (hrs)", value=float(ticket['resolution_time_hours']))

            if st.form_submit_button("Update"):
                update_ticket(update_id, status=upd_status, priority=upd_priority,
                              resolution_time_hours=upd_resolution)
                st.success("Ticket updated successfully")
                st.rerun()

    with col2:
        st.markdown("#### Delete Ticket")
        delete_id = st.selectbox("Select Ticket ID to Delete", df['ticket_id'].values, key="delete")
        st.markdown("")
        st.markdown("")
        if st.button("Delete Ticket", type="primary"):
            delete_ticket(delete_id)
            st.success("Ticket deleted successfully")
            st.rerun()

# Tab 2: Analysis
with tab2:
    # Staff performance at the top
    st.markdown("#### High-Value Insight: Staff Performance")

    staff_performance = df.groupby('assigned_to').agg({
        'ticket_id': 'count',
        'resolution_time_hours': 'mean'
    }).rename(columns={'ticket_id': 'total_tickets', 'resolution_time_hours': 'avg_resolution_time'})

    staff_performance = staff_performance.sort_values('avg_resolution_time', ascending=False)

    perf_col1, perf_col2 = st.columns([1, 2])

    with perf_col1:
        st.dataframe(staff_performance, use_container_width=True)
        slowest_staff = staff_performance['avg_resolution_time'].idxmax()
        slowest_time = staff_performance['avg_resolution_time'].max()
        st.warning(
            f"Performance Anomaly: {slowest_staff} has the highest average resolution time ({slowest_time:.1f} hours)")

    with perf_col2:
        fig = px.bar(staff_performance, x=staff_performance.index, y='avg_resolution_time',
                     labels={'x': 'Staff Member', 'avg_resolution_time': 'Avg Resolution Time (hrs)'},
                     title="Average Resolution Time by Staff")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Process bottleneck
    st.markdown("#### Process Bottleneck Analysis")
    status_resolution = df.groupby('status')['resolution_time_hours'].mean().sort_values(ascending=False)

    bottleneck_col1, bottleneck_col2 = st.columns([1, 2])

    with bottleneck_col1:
        st.dataframe(status_resolution, use_container_width=True)
        bottleneck_status = status_resolution.idxmax()
        bottleneck_time = status_resolution.max()
        st.info(
            f"Bottleneck Identified: Tickets in '{bottleneck_status}' status have the longest resolution time ({bottleneck_time:.1f} hours)")

    with bottleneck_col2:
        fig = px.bar(x=status_resolution.index, y=status_resolution.values,
                     labels={'x': 'Status', 'y': 'Avg Resolution Time (hrs)'},
                     title="Resolution Time by Status")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Additional charts
    st.markdown("#### Ticket Statistics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        priority_counts = df['priority'].value_counts()
        fig1 = px.bar(x=priority_counts.index, y=priority_counts.values,
                      labels={'x': 'Priority', 'y': 'Count'},
                      title="Ticket Priority Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        fig2 = px.box(df, x='priority', y='resolution_time_hours',
                      labels={'priority': 'Priority', 'resolution_time_hours': 'Resolution Time (hours)'},
                      title="Resolution Time Distribution by Priority")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("IT Operations Module - A.R.G.U.S.")