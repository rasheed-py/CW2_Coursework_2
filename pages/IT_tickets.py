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
# If not logged in, show error and stop the page from loading
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
# Only 'user' and 'it_admin' roles can access this dashboard
if st.session_state.role not in ["user", "it_admin"]:
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
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity", icon="🛡️")
    st.sidebar.page_link("pages/data_science.py", label="Data Science", icon="📊")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load ticket data from database
df = load_it_tickets()

# Main page title and description
st.title("IT Operations Dashboard")
st.markdown("### Service Desk Performance & Ticket Management")
st.markdown("---")

# Display key metrics at the top of the page
# Split into 4 columns for better layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Count total tickets
    st.metric("Total Tickets", len(df))
with col2:
    # Count tickets with 'Open' status
    open_tickets = len(df[df['status'] == 'Open'])
    st.metric("Open Tickets", open_tickets)
with col3:
    # Calculate average resolution time
    avg_resolution = df['resolution_time_hours'].mean()
    st.metric("Avg Resolution", f"{avg_resolution:.1f} hrs")
with col4:
    # Count critical priority tickets
    critical = len(df[df['priority'] == 'Critical'])
    st.metric("Critical", critical)

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Overview", "Tickets", "Analysis"])

# Tab 1: Overview with charts and visualizations
with tab1:
    st.subheader("Performance Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Create bar chart showing tickets by priority
        st.markdown("#### Tickets by Priority")
        priority_counts = df['priority'].value_counts()
        fig1 = px.bar(x=priority_counts.index, y=priority_counts.values,
                      labels={'x': 'Priority', 'y': 'Count'},
                      title="Ticket Priority Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Create pie chart showing ticket status distribution
        st.markdown("#### Ticket Status")
        status_counts = df['status'].value_counts()
        fig2 = px.pie(values=status_counts.values, names=status_counts.index,
                      title="Status Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # Bar chart showing staff workload
    st.markdown("#### Staff Workload")
    staff_counts = df['assigned_to'].value_counts()
    fig3 = px.bar(x=staff_counts.index, y=staff_counts.values,
                  labels={'x': 'Staff Member', 'y': 'Tickets Assigned'},
                  title="Tickets per Staff Member")
    st.plotly_chart(fig3, use_container_width=True)

# Tab 2: Ticket Management (CRUD operations)
with tab2:
    st.subheader("Ticket Management")

    # Create new ticket form (always visible, no dropdown)
    st.markdown("#### Create New Ticket")
    with st.form("create_ticket"):
        # Generate next available ticket ID
        new_id = st.number_input("Ticket ID", min_value=1, value=int(df['ticket_id'].max() + 1))
        # Dropdown for priority level
        new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        # Text area for ticket description
        new_description = st.text_area("Description")
        # Dropdown for ticket status
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"])
        # Dropdown to assign ticket to staff member
        new_assigned = st.selectbox("Assign To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
        # Get current timestamp for the ticket
        new_created = st.text_input("Created At", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Input for resolution time in hours
        new_resolution = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0)

        # Submit button for the form
        if st.form_submit_button("Create Ticket"):
            # Call function to create ticket in database
            create_ticket(new_id, new_priority, new_description, new_status,
                          new_assigned, new_created, new_resolution)
            st.success("Ticket created successfully")
            # Refresh the page to show new data
            st.rerun()

    st.markdown("---")

    # Display all tickets in a table (no filters)
    st.markdown("#### All Tickets")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections side by side
    col1, col2 = st.columns(2)

    with col1:
        # Update ticket section
        with st.expander("Update Ticket"):
            # Dropdown to select which ticket to update
            update_id = st.selectbox("Select Ticket ID", df['ticket_id'].values)
            # Get the selected ticket data
            ticket = df[df['ticket_id'] == update_id].iloc[0]

            with st.form("update_ticket"):
                # Dropdown for new status with current value pre-selected
                upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"],
                                          index=["Open", "In Progress", "Resolved", "Waiting for User"].index(
                                              ticket['status']))
                # Dropdown for new priority with current value pre-selected
                upd_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"],
                                            index=["Low", "Medium", "High", "Critical"].index(ticket['priority']))
                # Input for resolution time with current value
                upd_resolution = st.number_input("Resolution Time (hrs)", value=float(ticket['resolution_time_hours']))

                # Submit button to update
                if st.form_submit_button("Update"):
                    # Call function to update ticket in database
                    update_ticket(update_id, status=upd_status, priority=upd_priority,
                                  resolution_time_hours=upd_resolution)
                    st.success("Ticket updated successfully")
                    st.rerun()

    with col2:
        # Delete ticket section
        with st.expander("Delete Ticket"):
            # Dropdown to select which ticket to delete
            delete_id = st.selectbox("Select Ticket ID to Delete", df['ticket_id'].values, key="delete")

            # Delete button with warning styling
            if st.button("Delete Ticket", type="primary"):
                # Call function to delete ticket from database
                delete_ticket(delete_id)
                st.success("Ticket deleted successfully")
                st.rerun()

# Tab 3: Analysis and insights
with tab3:
    st.subheader("Performance Analysis")

    # High-value insight section for staff performance
    st.markdown("#### High-Value Insight: Staff Performance")

    # Calculate average resolution time per staff member
    staff_performance = df.groupby('assigned_to').agg({
        'ticket_id': 'count',
        'resolution_time_hours': 'mean'
    }).rename(columns={'ticket_id': 'total_tickets', 'resolution_time_hours': 'avg_resolution_time'})

    # Sort by resolution time (slowest first)
    staff_performance = staff_performance.sort_values('avg_resolution_time', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Display staff performance data
        st.markdown("**Average Resolution Time by Staff**")
        st.dataframe(staff_performance, use_container_width=True)

        # Identify the staff member with slowest resolution time
        slowest_staff = staff_performance['avg_resolution_time'].idxmax()
        slowest_time = staff_performance['avg_resolution_time'].max()
        st.warning(
            f"Performance Anomaly: {slowest_staff} has the highest average resolution time ({slowest_time:.1f} hours)")

    with col2:
        # Create bar chart for staff performance
        fig = px.bar(staff_performance, x=staff_performance.index, y='avg_resolution_time',
                     labels={'x': 'Staff Member', 'avg_resolution_time': 'Avg Resolution Time (hrs)'},
                     title="Average Resolution Time by Staff")
        st.plotly_chart(fig, use_container_width=True)

    # Process bottleneck analysis
    st.markdown("#### Process Bottleneck Analysis")

    # Calculate average resolution time by status
    status_resolution = df.groupby('status')['resolution_time_hours'].mean().sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Display status resolution times
        st.markdown("**Average Resolution Time by Status**")
        st.dataframe(status_resolution, use_container_width=True)

        # Identify the status with longest resolution time
        bottleneck_status = status_resolution.idxmax()
        bottleneck_time = status_resolution.max()
        st.info(
            f"Bottleneck Identified: Tickets in '{bottleneck_status}' status have the longest resolution time ({bottleneck_time:.1f} hours)")

    with col2:
        # Create bar chart for status resolution times
        fig = px.bar(x=status_resolution.index, y=status_resolution.values,
                     labels={'x': 'Status', 'y': 'Avg Resolution Time (hrs)'},
                     title="Resolution Time by Status")
        st.plotly_chart(fig, use_container_width=True)

    # Box plot showing priority vs resolution time
    st.markdown("#### Priority vs Resolution Time")
    fig = px.box(df, x='priority', y='resolution_time_hours',
                 labels={'priority': 'Priority', 'resolution_time_hours': 'Resolution Time (hours)'},
                 title="Resolution Time Distribution by Priority")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("IT Operations Module - A.R.G.U.S.")