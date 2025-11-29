import streamlit as st
from arg_database.connection import setup_database
from authy.security import validate_username, validate_password, register_user, login_user

# Page configuration
st.set_page_config(
    page_title="A.R.G.U.S.",
    page_icon="🅰️",
    layout="wide"
)

# Initialize database on first run
setup_database()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None


def show_login_page():
    """Display login and registration page"""

    # Center columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Logo
        st.image("arg.png", width=150)

        st.title("🅰️.R.G.U.S.")
        st.markdown("### Secure Government Research")
        st.markdown("---")

        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        # Login Tab
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("🚀 Login", use_container_width=True)

                if submit:
                    if not username or not password:
                        st.error("⚠️ Please fill in all fields")
                    else:
                        success, result = login_user(username, password)
                        if success:
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

                if register:
                    if not new_username or not new_password or not confirm_password:
                        st.error("⚠️ Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        # Validate username
                        valid_user, user_msg = validate_username(new_username)
                        if not valid_user:
                            st.error(f"❌ {user_msg}")
                        else:
                            # Validate password
                            valid_pass, pass_msg = validate_password(new_password)
                            if not valid_pass:
                                st.error(f"❌ {pass_msg}")
                            else:
                                # Register user
                                success, result = register_user(new_username, new_password, role)
                                if success:
                                    st.success("✅ Registration successful! Please login.")
                                else:
                                    st.error(f"❌ {result}")


def main():
    """Main application controller"""
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Redirect to dashboard page
        st.switch_page("pages\dashboard.py")


if __name__ == "__main__":
    main()