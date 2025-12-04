import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_datasets_metadata, create_dataset, update_dataset, delete_dataset
)

# Page configuration
st.set_page_config(
    page_title="Data Science Dashboard",
    page_icon="📊",
    layout="wide"
)

# Check if user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("⚠️ Please login first")
    st.stop()

# Check role access
if st.session_state.role not in ["user", "data_scientist"]:
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
    st.sidebar.page_link("pages/IT_tickets.py", label="💻 IT Operations", icon="💻")

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load data
df = load_datasets_metadata()

# Main content
st.title("📊 Data Science Dashboard")
st.markdown("### Dataset Management & Analytics")
st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Datasets", len(df))
with col2:
    total_rows = df['rows'].sum()
    st.metric("Total Rows", f"{total_rows:,}")
with col3:
    # Estimate storage (assuming avg 1KB per row)
    storage_gb = (total_rows * 1000) / (1024 ** 3)
    st.metric("Est. Storage", f"{storage_gb:.2f} GB")
with col4:
    sources = df['uploaded_by'].nunique()
    st.metric("Data Sources", sources)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Datasets", "🔍 Analysis"])

with tab1:
    st.subheader("Dataset Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Dataset size distribution
        st.markdown("#### Dataset Size Distribution")
        fig1 = px.bar(df, x='name', y='rows',
                      title="Rows per Dataset",
                      labels={'name': 'Dataset', 'rows': 'Number of Rows'})
        fig1.update_xaxis(tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Source breakdown
        st.markdown("#### Data Sources")
        source_counts = df['uploaded_by'].value_counts()
        fig2 = px.pie(values=source_counts.values, names=source_counts.index,
                      title="Datasets by Source")
        st.plotly_chart(fig2, use_container_width=True)

    # Column distribution
    st.markdown("#### Dataset Complexity")
    fig3 = px.scatter(df, x='rows', y='columns', size='rows',
                      hover_data=['name'], title="Rows vs Columns",
                      labels={'rows': 'Number of Rows', 'columns': 'Number of Columns'})
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Dataset Management")

    # Add new dataset
    with st.expander("➕ Add New Dataset"):
        with st.form("create_dataset"):
            new_id = st.number_input("Dataset ID", min_value=1, value=int(df['dataset_id'].max() + 1))
            new_name = st.text_input("Dataset Name")
            new_rows = st.number_input("Number of Rows", min_value=0, value=1000)
            new_columns = st.number_input("Number of Columns", min_value=1, value=10)
            new_uploaded_by = st.selectbox("Uploaded By", ["data_scientist", "cyber_admin", "it_admin"])
            new_upload_date = st.date_input("Upload Date", value=datetime.now())

            if st.form_submit_button("Add Dataset"):
                create_dataset(new_id, new_name, new_rows, new_columns, new_uploaded_by, str(new_upload_date))
                st.success("✅ Dataset added!")
                st.rerun()

    # View all datasets
    st.markdown("#### All Datasets")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_source = st.multiselect("Filter by Source", df['uploaded_by'].unique(),
                                       default=df['uploaded_by'].unique())
    with col2:
        min_rows = st.number_input("Minimum Rows", min_value=0, value=0)

    # Apply filters
    filtered_df = df[
        (df['uploaded_by'].isin(filter_source)) &
        (df['rows'] >= min_rows)
        ]

    st.dataframe(filtered_df, use_container_width=True)

    # Update/Delete operations
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("✏️ Update Dataset"):
            update_id = st.selectbox("Select Dataset ID", df['dataset_id'].values)
            dataset = df[df['dataset_id'] == update_id].iloc[0]

            with st.form("update_dataset"):
                upd_name = st.text_input("Name", value=dataset['name'])
                upd_rows = st.number_input("Rows", value=int(dataset['rows']))
                upd_columns = st.number_input("Columns", value=int(dataset['columns']))

                if st.form_submit_button("Update"):
                    update_dataset(update_id, name=upd_name, rows=upd_rows, columns=upd_columns)
                    st.success("✅ Dataset updated!")
                    st.rerun()

    with col2:
        with st.expander("🗑️ Delete Dataset"):
            delete_id = st.selectbox("Select Dataset ID to Delete", df['dataset_id'].values, key="delete")

            if st.button("Delete Dataset", type="primary"):
                delete_dataset(delete_id)
                st.success("✅ Dataset deleted!")
                st.rerun()

with tab3:
    st.subheader("Data Governance Analysis")

    # Resource consumption
    st.markdown("#### 🎯 High-Value Insight: Resource Consumption")

    col1, col2 = st.columns(2)

    with col1:
        # Largest datasets
        st.markdown("**Largest Datasets**")
        top_datasets = df.nlargest(3, 'rows')[['name', 'rows', 'uploaded_by']]
        st.dataframe(top_datasets, use_container_width=True)

    with col2:
        # Source dependency
        st.markdown("**Source Dependency**")
        source_rows = df.groupby('uploaded_by')['rows'].sum().sort_values(ascending=False)
        fig = px.bar(x=source_rows.index, y=source_rows.values,
                     labels={'x': 'Source', 'y': 'Total Rows'})
        st.plotly_chart(fig, use_container_width=True)

    # Archiving recommendations
    st.markdown("#### 📋 Data Governance Recommendations")

    # Identify large datasets for archiving
    large_threshold = df['rows'].quantile(0.75)
    large_datasets = df[df['rows'] > large_threshold]

    st.info(
        f"💡 **Archiving Policy Recommendation**: {len(large_datasets)} datasets exceed the 75th percentile ({large_threshold:,.0f} rows) and should be considered for archiving or compression.")

    if len(large_datasets) > 0:
        st.markdown("**Datasets Recommended for Archiving:**")
        st.dataframe(large_datasets[['name', 'rows', 'uploaded_by', 'upload_date']], use_container_width=True)

    # Source analysis
    st.markdown("#### 📊 Source Dependency Analysis")
    total_by_source = df.groupby('uploaded_by').agg({
        'dataset_id': 'count',
        'rows': 'sum'
    }).rename(columns={'dataset_id': 'dataset_count', 'rows': 'total_rows'})

    st.dataframe(total_by_source, use_container_width=True)

st.markdown("---")
st.caption("📊 Data Science Module - A.R.G.U.S.")