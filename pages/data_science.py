import streamlit as st
import plotly.express as px
from pathlib import Path
import base64
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
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please login first")
    st.stop()

# Check if user has permission to view this page
if st.session_state.role not in ["user", "data_scientist"]:
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

    # Minimal CSS - just background and content overlay
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
    st.sidebar.page_link("pages/cybersecurity.py", label="Cybersecurity")
    st.sidebar.page_link("pages/IT_tickets.py", label="IT Operations")
    st.sidebar.page_link("pages/ai_assistant.py", label="AI assistant")

st.sidebar.markdown("---")

# Logout button functionality
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.switch_page("arg_app.py")

# Load dataset metadata from database
df = load_datasets_metadata()

# Main page title
st.title("Data Science Dashboard")
st.markdown("### Dataset Management & Analytics")

# Display key metrics in a 2x2 grid
st.markdown("#### System Overview")
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.metric("Total Datasets", len(df))
with row1_col2:
    total_rows = df['rows'].sum()
    st.metric("Total Rows", f"{total_rows:,}")

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    storage_gb = (total_rows * 1000) / (1024 ** 3)
    st.metric("Est. Storage", f"{storage_gb:.2f} GB")
with row2_col2:
    sources = df['uploaded_by'].nunique()
    st.metric("Data Sources", sources)

st.markdown("---")

# Create tabs - only Datasets and Analysis
tab1, tab2 = st.tabs(["Dataset Management", "Governance Analysis"])

# Tab 1: Dataset Management
with tab1:
    # Add new dataset form (always visible)
    st.markdown("#### Add New Dataset")
    with st.form("create_dataset"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_id = st.number_input("Dataset ID", min_value=1, value=int(df['dataset_id'].max() + 1))
            new_name = st.text_input("Dataset Name")
        with col2:
            new_rows = st.number_input("Number of Rows", min_value=0, value=1000)
            new_columns = st.number_input("Number of Columns", min_value=1, value=10)
        with col3:
            new_uploaded_by = st.selectbox("Uploaded By", ["data_scientist", "cyber_admin", "it_admin"])
            new_upload_date = st.date_input("Upload Date", value=datetime.now())

        if st.form_submit_button("Add Dataset"):
            create_dataset(new_id, new_name, new_rows, new_columns, new_uploaded_by, str(new_upload_date))
            st.success("Dataset added successfully")
            st.rerun()

    st.markdown("---")

    # Display all datasets
    st.markdown("#### All Datasets")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Update and Delete sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Update Dataset")
        update_id = st.selectbox("Select Dataset ID", df['dataset_id'].values)
        dataset = df[df['dataset_id'] == update_id].iloc[0]

        with st.form("update_dataset"):
            upd_name = st.text_input("Name", value=dataset['name'])
            upd_rows = st.number_input("Rows", value=int(dataset['rows']))
            upd_columns = st.number_input("Columns", value=int(dataset['columns']))

            if st.form_submit_button("Update"):
                update_dataset(update_id, name=upd_name, rows=upd_rows, columns=upd_columns)
                st.success("Dataset updated successfully")
                st.rerun()

    with col2:
        st.markdown("#### Delete Dataset")
        delete_id = st.selectbox("Select Dataset ID to Delete", df['dataset_id'].values, key="delete")
        st.markdown("")
        st.markdown("")
        if st.button("Delete Dataset", type="primary"):
            delete_dataset(delete_id)
            st.success("Dataset deleted successfully")
            st.rerun()

# Tab 2: Analysis
with tab2:
    # Resource consumption at the top
    st.markdown("#### High-Value Insight: Resource Consumption")

    resource_col1, resource_col2 = st.columns([1, 2])

    with resource_col1:
        top_datasets = df.nlargest(3, 'rows')[['name', 'rows', 'uploaded_by']]
        st.dataframe(top_datasets, use_container_width=True)

    with resource_col2:
        source_rows = df.groupby('uploaded_by')['rows'].sum().sort_values(ascending=False)
        fig = px.bar(x=source_rows.index, y=source_rows.values,
                     labels={'x': 'Source', 'y': 'Total Rows'},
                     title="Source Dependency")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Data governance recommendations
    st.markdown("#### Data Governance Recommendations")

    large_threshold = df['rows'].quantile(0.75)
    large_datasets = df[df['rows'] > large_threshold]

    st.info(
        f"Archiving Policy Recommendation: {len(large_datasets)} datasets exceed the 75th percentile ({large_threshold:,.0f} rows) and should be considered for archiving or compression.")

    if len(large_datasets) > 0:
        st.dataframe(large_datasets[['name', 'rows', 'uploaded_by', 'upload_date']], use_container_width=True)

    st.markdown("---")

    # Dataset statistics
    st.markdown("#### Dataset Statistics")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig1 = px.bar(df, x='name', y='rows',
                      title="Rows per Dataset",
                      labels={'name': 'Dataset', 'rows': 'Number of Rows'})
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    with chart_col2:
        fig2 = px.scatter(df, x='rows', y='columns', size='rows',
                          hover_data=['name'], title="Dataset Complexity",
                          labels={'rows': 'Number of Rows', 'columns': 'Number of Columns'})
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Source dependency analysis
    st.markdown("#### Source Dependency Analysis")
    total_by_source = df.groupby('uploaded_by').agg({
        'dataset_id': 'count',
        'rows': 'sum'
    }).rename(columns={'dataset_id': 'dataset_count', 'rows': 'total_rows'})

    st.dataframe(total_by_source, use_container_width=True)

st.markdown("---")
st.caption("Data Science Module - A.R.G.U.S.")