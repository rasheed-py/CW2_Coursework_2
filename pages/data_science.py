import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from arg_database.data_loader import (
    load_datasets_metadata, create_dataset, update_dataset, delete_dataset
)

# Set up the page configuration
st.set_page_config(
    page_title="Data Science Dashboard",
    page_icon="📊",
    layout="wide"
)

# Check if the user is logged in
# If not logged in, show error and stop the page from loading
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
# Only 'user' and 'data_scientist' roles can access this dashboard
if st.session_state.role not in ["user", "data_scientist"]:
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
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations", icon="💻")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("login.py")

# Load dataset metadata from database
df = load_datasets_metadata()

# Main page title and description
st.title("Data Science Dashboard")
st.markdown("### Dataset Management & Analytics")
st.markdown("---")

# Display key metrics at the top of the page
# Split into 4 columns for better layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Count total number of datasets
    st.metric("Total Datasets", len(df))
with col2:
    # Sum all rows across all datasets
    total_rows = df['rows'].sum()
    st.metric("Total Rows", f"{total_rows:,}")
with col3:
    # Estimate storage size (assuming 1KB per row)
    storage_gb = (total_rows * 1000) / (1024 ** 3)
    st.metric("Est. Storage", f"{storage_gb:.2f} GB")
with col4:
    # Count unique data sources
    sources = df['uploaded_by'].nunique()
    st.metric("Data Sources", sources)

st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Overview", "Datasets", "Analysis"])

# Tab 1: Overview with charts and visualizations
with tab1:
    st.subheader("Dataset Overview")

    col1, col2 = st.columns(2)

    with col1:
        # Create bar chart showing dataset sizes
        st.markdown("#### Dataset Size Distribution")
        fig1 = px.bar(df, x='name', y='rows',
                      title="Rows per Dataset",
                      labels={'name': 'Dataset', 'rows': 'Number of Rows'})
        # Rotate x-axis labels for better readability
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Create pie chart showing data source breakdown
        st.markdown("#### Data Sources")
        source_counts = df['uploaded_by'].value_counts()
        fig2 = px.pie(values=source_counts.values, names=source_counts.index,
                      title="Datasets by Source")
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter plot showing dataset complexity
    st.markdown("#### Dataset Complexity")
    fig3 = px.scatter(df, x='rows', y='columns', size='rows',
                      hover_data=['name'], title="Rows vs Columns",
                      labels={'rows': 'Number of Rows', 'columns': 'Number of Columns'})
    st.plotly_chart(fig3, use_container_width=True)

# Tab 2: Dataset Management (CRUD operations)
with tab2:
    st.subheader("Dataset Management")

    # Add new dataset section (always visible, no dropdown)
    st.markdown("#### Add New Dataset")
    with st.form("create_dataset"):
        # Generate next available dataset ID
        new_id = st.number_input("Dataset ID", min_value=1, value=int(df['dataset_id'].max() + 1))
        # Input for dataset name
        new_name = st.text_input("Dataset Name")
        # Input for number of rows
        new_rows = st.number_input("Number of Rows", min_value=0, value=1000)
        # Input for number of columns
        new_columns = st.number_input("Number of Columns", min_value=1, value=10)
        # Dropdown to select who uploaded the dataset
        new_uploaded_by = st.selectbox("Uploaded By", ["data_scientist", "cyber_admin", "it_admin"])
        # Date picker for upload date
        new_upload_date = st.date_input("Upload Date", value=datetime.now())

        # Submit button for the form
        if st.form_submit_button("Add Dataset"):
            # Call function to create dataset in database
            create_dataset(new_id, new_name, new_rows, new_columns, new_uploaded_by, str(new_upload_date))
            st.success("Dataset added successfully")
            # Refresh the page to show new data
            st.rerun()

    st.markdown("---")

    # Display all datasets section
    st.markdown("#### All Datasets")

    # Display all datasets in table (no filters)
    st.dataframe(df, use_container_width=True)

    # Update and Delete sections side by side
    col1, col2 = st.columns(2)

    with col1:
        # Update dataset section
        with st.expander("Update Dataset"):
            # Dropdown to select which dataset to update
            update_id = st.selectbox("Select Dataset ID", df['dataset_id'].values)
            # Get the selected dataset data
            dataset = df[df['dataset_id'] == update_id].iloc[0]

            with st.form("update_dataset"):
                # Input fields with current values
                upd_name = st.text_input("Name", value=dataset['name'])
                upd_rows = st.number_input("Rows", value=int(dataset['rows']))
                upd_columns = st.number_input("Columns", value=int(dataset['columns']))

                # Submit button to update
                if st.form_submit_button("Update"):
                    # Call function to update dataset in database
                    update_dataset(update_id, name=upd_name, rows=upd_rows, columns=upd_columns)
                    st.success("Dataset updated successfully")
                    st.rerun()

    with col2:
        # Delete dataset section
        with st.expander("Delete Dataset"):
            # Dropdown to select which dataset to delete
            delete_id = st.selectbox("Select Dataset ID to Delete", df['dataset_id'].values, key="delete")

            # Delete button with warning styling
            if st.button("Delete Dataset", type="primary"):
                # Call function to delete dataset from database
                delete_dataset(delete_id)
                st.success("Dataset deleted successfully")
                st.rerun()

# Tab 3: Analysis and insights
with tab3:
    st.subheader("Data Governance Analysis")

    # High-value insight section for resource consumption
    st.markdown("#### High-Value Insight: Resource Consumption")

    col1, col2 = st.columns(2)

    with col1:
        # Display the 3 largest datasets
        st.markdown("**Largest Datasets**")
        top_datasets = df.nlargest(3, 'rows')[['name', 'rows', 'uploaded_by']]
        st.dataframe(top_datasets, use_container_width=True)

    with col2:
        # Create bar chart showing total rows by source
        st.markdown("**Source Dependency**")
        source_rows = df.groupby('uploaded_by')['rows'].sum().sort_values(ascending=False)
        fig = px.bar(x=source_rows.index, y=source_rows.values,
                     labels={'x': 'Source', 'y': 'Total Rows'})
        st.plotly_chart(fig, use_container_width=True)

    # Data governance recommendations section
    st.markdown("#### Data Governance Recommendations")

    # Calculate threshold for large datasets (75th percentile)
    large_threshold = df['rows'].quantile(0.75)
    # Filter datasets above threshold
    large_datasets = df[df['rows'] > large_threshold]

    # Display recommendation message
    st.info(
        f"Archiving Policy Recommendation: {len(large_datasets)} datasets exceed the 75th percentile ({large_threshold:,.0f} rows) and should be considered for archiving or compression.")

    # Show list of datasets recommended for archiving
    if len(large_datasets) > 0:
        st.markdown("**Datasets Recommended for Archiving:**")
        st.dataframe(large_datasets[['name', 'rows', 'uploaded_by', 'upload_date']], use_container_width=True)

    # Source dependency analysis section
    st.markdown("#### Source Dependency Analysis")
    # Group by source and calculate totals
    total_by_source = df.groupby('uploaded_by').agg({
        'dataset_id': 'count',
        'rows': 'sum'
    }).rename(columns={'dataset_id': 'dataset_count', 'rows': 'total_rows'})

    # Display the aggregated data
    st.dataframe(total_by_source, use_container_width=True)

st.markdown("---")
st.caption("Data Science Module - A.R.G.U.S.")