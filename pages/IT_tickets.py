import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_it_tickets, create_ticket, update_ticket, delete_ticket
)

# Page configuration
st.set_page_config(
    page_title="IT Operations Dashboard",
    page_icon="💻",
    layout="wide"
)

# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first")
    st.stop()

# Check role access
if st.session_state.role not in ["user", "it_admin"]:
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
    st.sidebar.page_link("pages/cybersecurity.py", label="🛡️ Cybersecurity", icon="🛡️")
    st.sidebar.page_link("pages/data_science.py", label="📊 Data Science", icon="📊")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load data
df = load_it_tickets()

# Main content
st.title("💻 IT Operations Dashboard")
st.markdown("### Service Desk Performance & Ticket Management")
st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", len(df))
with col2:
    open_tickets = len(df[df['status'] == 'Open'])
    st.metric("Open Tickets", open_tickets)
with col3:
    avg_resolution = df['resolution_time_hours'].mean()
    st.metric("Avg Resolution", f"{avg_resolution:.1f} hrs")
with col4:
    critical = len(df[df['priority'] == 'Critical'])
    st.metric("Critical", critical)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Tickets", "🔍 Analysis"])

with tab1:
    st.subheader("Performance Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Priority distribution
        st.markdown("#### Tickets by Priority")
        priority_counts = df['priority'].value_counts()
        fig1 = px.bar(x=priority_counts.index, y=priority_counts.values,
                      labels={'x': 'Priority', 'y': 'Count'},
                      title="Ticket Priority Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Status distribution
        st.markdown("#### Ticket Status")
        status_counts = df['status'].value_counts()
        fig2 = px.pie(values=status_counts.values, names=status_counts.index,
                      title="Status Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # Staff workload
    st.markdown("#### Staff Workload")
    staff_counts = df['assigned_to'].value_counts()
    fig3 = px.bar(x=staff_counts.index, y=staff_counts.values,
                  labels={'x': 'Staff Member', 'y': 'Tickets Assigned'},
                  title="Tickets per Staff Member")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Ticket Management")

    # Create new ticket
    with st.expander("➕ Create New Ticket"):
        with st.form("create_ticket"):
            new_id = st.number_input("Ticket ID", min_value=1, value=int(df['ticket_id'].max() + 1))
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            new_description = st.text_area("Description")
            new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Waiting for User"])
            new_assigned = st.selectbox("Assign To", ["IT_Support_A", "IT_Support_B", "IT_Support_C"])
            new_created = st.text_input("Created At", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            new_resolution = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0)

            if st.form_submit_button("Create Ticket"):
                create_ticket(new_id, new_priority, new_description, new_status,
                              new_assigned, new_created, new_resolution)
                st.success("✅ Ticket created!")
                st.rerun()

    # View all tickets
    st.markdown("#### All Tickets")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.multiselect("Filter by Status", df['status'].unique(),
                                       default=df['status'].unique())
    with col2:
        filter_priority = st.multiselect("Filter by Priority", df['priority'].unique(),
                                         default=df['priority'].unique())
    with col3:
        filter_staff = st.multiselect("Filter by Staff", df['assigned_to'].unique(),
                                      default=df['assigned_to'].unique())

    # Apply filters
    filtered_df = df[
        (df['status'].isin(filter_status)) &
        (df['priority'].isin(filter_priority)) &
        (df['assigned_to'].isin(filter_staff))
        ]

    st.dataframe(filtered_df, use_container_width=True)

    # Update/Delete operations
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("✏️ Update Ticket"):
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
                    st.success("✅ Ticket updated!")
                    st.rerun()

    with col2:
        with st.expander("🗑️ Delete Ticket"):
            delete_id = st.selectbox("Select Ticket ID to Delete", df['ticket_id'].values, key="delete")

            if st.button("Delete Ticket", type="primary"):
                delete_ticket(delete_id)
                st.success("✅ Ticket deleted!")
                st.rerun()

with tab3:
    st.subheader("Performance Analysis")

    # Staff performance analysis
    st.markdown("#### 🎯 High-Value Insight: Staff Performance")

    staff_performance = df.groupby('assigned_to').agg({
        'ticket_id': 'count',
        'resolution_time_hours': 'mean'
    }).rename(columns={'ticket_id': 'total_tickets', 'resolution_time_hours': 'avg_resolution_time'})

    staff_performance = staff_performance.sort_values('avg_resolution_time', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Average Resolution Time by Staff**")
        st.dataframe(staff_performance, use_container_width=True)

        # Identify slowest staff
        slowest_staff = staff_performance['avg_resolution_time'].idxmax()
        slowest_time = staff_performance['avg_resolution_time'].max()
        st.warning(
            f"⚠️ **Performance Anomaly**: {slowest_staff} has the highest average resolution time ({slowest_time:.1f} hours)")

    with col2:
        fig = px.bar(staff_performance, x=staff_performance.index, y='avg_resolution_time',
                     labels={'x': 'Staff Member', 'avg_resolution_time': 'Avg Resolution Time (hrs)'},
                     title="Average Resolution Time by Staff")
        st.plotly_chart(fig, use_container_width=True)

    # Status bottleneck analysis
    st.markdown("#### ⏱️ Process Bottleneck Analysis")

    status_resolution = df.groupby('status')['resolution_time_hours'].mean().sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Average Resolution Time by Status**")
        st.dataframe(status_resolution, use_container_width=True)

        # Identify bottleneck status
        bottleneck_status = status_resolution.idxmax()
        bottleneck_time = status_resolution.max()
        st.info(
            f"💡 **Bottleneck Identified**: Tickets in '{bottleneck_status}' status have the longest resolution time ({bottleneck_time:.1f} hours)")

    with col2:
        fig = px.bar(x=status_resolution.index, y=status_resolution.values,
                     labels={'x': 'Status', 'y': 'Avg Resolution Time (hrs)'},
                     title="Resolution Time by Status")
        st.plotly_chart(fig, use_container_width=True)

    # Priority vs Resolution Time
    st.markdown("#### 📊 Priority vs Resolution Time")
    fig = px.box(df, x='priority', y='resolution_time_hours',
                 labels={'priority': 'Priority', 'resolution_time_hours': 'Resolution Time (hours)'},
                 title="Resolution Time Distribution by Priority")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("💻 IT Operations Module - A.R.G.U.S.")