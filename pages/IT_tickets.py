import streamlit as st
import plotly.express as px
from pathlib import Path
import base64
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_it_tickets, create_ticket, update_ticket, delete_ticket
)

# Configure the Streamlit page settings
st.set_page_config(
    page_title="IT Operations Dashboard",
    page_icon="💻",
    layout="wide"
)

# Check if user is logged in - redirect to login if not
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
if st.session_state.role not in ["user", "it_admin"]:
    st.error("Access Denied - You don't have permission to view this page")
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
st.sidebar.write(f"**User:** {st.session_state.username}")
st.sidebar.write(f"**Role:** {st.session_state.role}")

# Add navigation links based on user role
st.sidebar.page_link("pages/dash.py", label="Dashboard")
if st.session_state.role == "user":
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/data_science.py", label="Data Science")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")

st.sidebar.markdown("---")

# Logout button - clears session state and returns to login
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
    # Calculate average resolution time across all tickets
    avg_resolution = df['resolution_time_hours'].mean()
    st.metric("Avg Resolution", f"{avg_resolution:.1f} hrs")
with row2_col2:
    st.metric("Critical", len(df[df['priority'] == 'Critical']))

st.markdown("---")

# Create tabs for ticket management and performance analysis
tab1, tab2 = st.tabs(["Ticket Management", "Performance Analysis"])

# Tab 1: Ticket Management
with tab1:
    # Form to create new ticket
    st.markdown("#### Create New Ticket")
    with st.form("create_ticket"):
        col1, col2, col3 = st.columns(3)
        with col1:
            # Generate next available ticket ID
            new_id = st.number_input("Ticket ID", min_value=1, value=int(df['ticket_id'].max() + 1))
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        with col2:
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"])
            new_assigned = st.selectbox("Assign To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
        with col3:
            # Default to current timestamp
            new_created = st.text_input("Created At", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            new_resolution = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0)

        new_description = st.text_area("Description")

        # Submit button - creates ticket in database
        if st.form_submit_button("Create Ticket"):
            create_ticket(new_id, new_priority, new_description, new_status,
                          new_assigned, new_created, new_resolution)
            st.success("Ticket created successfully")
            st.rerun()

    st.markdown("---")

    # Display all tickets in a table
    st.markdown("#### All Tickets")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections side by side
    col1, col2 = st.columns(2)

    with col1:
        # Update ticket form
        st.markdown("#### Update Ticket")
        update_id = st.selectbox("Select Ticket ID", df['ticket_id'].values)
        # Get the selected ticket's current data
        ticket = df[df['ticket_id'] == update_id].iloc[0]

        with st.form("update_ticket"):
            # Pre-populate fields with current values
            upd_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"],
                                      index=["Open", "In Progress", "Resolved", "Waiting for User"].index(
                                          ticket['status']))
            upd_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"],
                                        index=["Low", "Medium", "High", "Critical"].index(ticket['priority']))
            upd_resolution = st.number_input("Resolution Time (hrs)", value=float(ticket['resolution_time_hours']))

            # Submit button - updates ticket in database
            if st.form_submit_button("Update"):
                update_ticket(update_id, status=upd_status, priority=upd_priority,
                              resolution_time_hours=upd_resolution)
                st.success("Ticket updated successfully")
                st.rerun()

    with col2:
        # Delete ticket section
        st.markdown("#### Delete Ticket")
        delete_id = st.selectbox("Select Ticket ID to Delete", df['ticket_id'].values, key="delete")
        st.markdown("")
        st.markdown("")
        # Delete button - removes ticket from database
        if st.button("Delete Ticket", type="primary"):
            delete_ticket(delete_id)
            st.success("Ticket deleted successfully")
            st.rerun()

# Tab 2: Performance Analysis
with tab2:
    # Staff performance analysis - highest priority insight
    st.markdown("#### High-Value Insight: Staff Performance")

    # Aggregate performance metrics by staff member
    staff_performance = df.groupby('assigned_to').agg({
        'ticket_id': 'count',
        'resolution_time_hours': 'mean'
    }).rename(columns={'ticket_id': 'total_tickets', 'resolution_time_hours': 'avg_resolution_time'})

    # Sort by average resolution time (descending)
    staff_performance = staff_performance.sort_values('avg_resolution_time', ascending=False)

    perf_col1, perf_col2 = st.columns([1, 2])

    with perf_col1:
        # Display staff performance table
        st.dataframe(staff_performance, use_container_width=True)
        # Identify slowest staff member
        slowest_staff = staff_performance['avg_resolution_time'].idxmax()
        slowest_time = staff_performance['avg_resolution_time'].max()
        st.warning(
            f"Performance Anomaly: {slowest_staff} has the highest average resolution time ({slowest_time:.1f} hours)")

    with perf_col2:
        # Bar chart of average resolution time by staff
        fig = px.bar(staff_performance, x=staff_performance.index, y='avg_resolution_time',
                     labels={'x': 'Staff Member', 'avg_resolution_time': 'Avg Resolution Time (hrs)'},
                     title="Average Resolution Time by Staff")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Process bottleneck analysis
    st.markdown("#### Process Bottleneck Analysis")
    # Calculate average resolution time by ticket status
    status_resolution = df.groupby('status')['resolution_time_hours'].mean().sort_values(ascending=False)

    bottleneck_col1, bottleneck_col2 = st.columns([1, 2])

    with bottleneck_col1:
        # Display status resolution time table
        st.dataframe(status_resolution, use_container_width=True)
        # Identify bottleneck status
        bottleneck_status = status_resolution.idxmax()
        bottleneck_time = status_resolution.max()
        st.info(
            f"Bottleneck Identified: Tickets in '{bottleneck_status}' status have the longest resolution time ({bottleneck_time:.1f} hours)")

    with bottleneck_col2:
        # Bar chart of resolution time by status
        fig = px.bar(x=status_resolution.index, y=status_resolution.values,
                     labels={'x': 'Status', 'y': 'Avg Resolution Time (hrs)'},
                     title="Resolution Time by Status")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Additional ticket statistics
    st.markdown("#### Ticket Statistics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Bar chart of ticket priority distribution
        priority_counts = df['priority'].value_counts()
        fig1 = px.bar(x=priority_counts.index, y=priority_counts.values,
                      labels={'x': 'Priority', 'y': 'Count'},
                      title="Ticket Priority Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        # Box plot showing resolution time distribution by priority
        fig2 = px.box(df, x='priority', y='resolution_time_hours',
                      labels={'priority': 'Priority', 'resolution_time_hours': 'Resolution Time (hours)'},
                      title="Resolution Time Distribution by Priority")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("IT Operations Module - A.R.G.U.S.")