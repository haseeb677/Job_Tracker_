import streamlit as st
from database import register_user, authenticate_user

def login():
    st.subheader("🔐 Login to Continue")
    tab1, tab2 = st.tabs(["🔓 Login", "🆕 Register"])

    with tab1:
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔑 Password", type="password", key="login_pass")
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = {"id": user["id"], "email": user["email"]}
                st.success("✅ Login successful")
                st.rerun()  # Safe rerun
            else:
                st.error("❌ Invalid credentials. Try again.")

    with tab2:
        new_email = st.text_input("📧 New Email", key="register_email")
        new_pass = st.text_input("🔑 New Password", type="password", key="register_pass")
        if st.button("Register"):
            if new_email and new_pass:
                success = register_user(new_email, new_pass)
                if success:
                    st.success("✅ Registered! Now login.")
                else:
                    st.error("⚠️ Email already exists.")
            else:
                st.warning("❗ Please enter both email and password.")

def logout():
    st.sidebar.markdown(f"👋 Logged in as `{st.session_state.user['email']}`")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()