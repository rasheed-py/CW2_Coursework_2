import streamlit as st
from arg_database.connection import setup_database
from authy.security import validate_username, validate_password, register_user, login_user
from pathlib import Path
import base64

# Configure the Streamlit page settings
st.set_page_config(
    page_title=".R.G.U.S.",
    page_icon="🅰️",
    layout="wide"
)

# Initialize database on first run
setup_database()

# Initialize session state variables for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

# Path to background image
image_path = "imgs/backdrop.jpg"

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


def show_login_page():
    """Display login and registration page"""

    # Create centered layout with 3 columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Display logo
        st.image("imgs/arg.png", width=150)

        # Page title and header
        st.title("🅰️.R.G.U.S.")
        st.markdown("### Secure Government Research")
        st.markdown("---")

        # Create tabs for Login and Register
        tab1, tab2 = st.tabs([" Login", " Register"])

        # Login Tab
        with tab1:
            with st.form("login_form"):
                # Input fields for login
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button(" Login", use_container_width=True)

                # Handle login submission
                if submit:
                    if not username or not password:
                        st.error("⚠️ Please fill in all fields")
                    else:
                        # Attempt to authenticate user
                        success, result = login_user(username, password)
                        if success:
                            # Set session state on successful login
                            st.session_state.logged_in = True
                            st.session_state.username = result['username']
                            st.session_state.role = result['role']
                            st.success(f"✅ Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")

        # Register Tab
        with tab2:
            with st.form("register_form"):
                # Input fields for registration
                new_username = st.text_input("Username", key="reg_user",
                                             placeholder="Choose a username",
                                             help="3-20 alphanumeric characters")
                new_password = st.text_input("Password", type="password", key="reg_pass",
                                             placeholder="Create a strong password",
                                             help="Min 6 chars, include uppercase, lowercase, and number")
                confirm_password = st.text_input("Confirm Password", type="password",
                                                 placeholder="Re-enter your password")
                role = st.selectbox("Select Your Role",
                                    ["user", "cybersecurity", "data_scientist", "it_admin"],
                                    help="Choose your domain (select 'user' for general access)")
                register = st.form_submit_button("✨ Create Account", use_container_width=True)

                # Handle registration submission
                if register:
                    if not new_username or not new_password or not confirm_password:
                        st.error("⚠️ Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        # Validate username format
                        valid_user, user_msg = validate_username(new_username)
                        if not valid_user:
                            st.error(f"❌ {user_msg}")
                        else:
                            # Validate password strength
                            valid_pass, pass_msg = validate_password(new_password)
                            if not valid_pass:
                                st.error(f"❌ {pass_msg}")
                            else:
                                # Register user in database
                                success, result = register_user(new_username, new_password, role)
                                if success:
                                    st.success("✅ Registration successful! Please login.")
                                else:
                                    st.error(f"❌ {result}")


def main():
    """Main application controller"""
    if not st.session_state.logged_in:
        # Show login page if user is not authenticated
        show_login_page()
    else:
        # Redirect to dashboard page if user is logged in
        st.switch_page("pages\dash.py")


if __name__ == "__main__":
    main()