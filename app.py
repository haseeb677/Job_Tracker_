import streamlit as st
import os
import datetime
import pandas as pd
from database import create_tables, add_job, view_jobs, update_job, delete_job, update_job_status
from auth import login, logout
from utils import search_jobs
from notifier import send_email
import plotly.express as px

# Setup
st.set_page_config(page_title="Job Application Tracker", page_icon="🗂️", layout="wide")
st.title("🗂️ Job Application Tracker")

# --- Session Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Ensure DB tables exist
create_tables()

# --- Login Flow ---
if not st.session_state['logged_in'] or st.session_state['user'] is None:
    login()  # This should set st.session_state['logged_in'] and st.session_state['user']
    st.stop()
else:
    logout()

# --- Safely access user session data ---
try:
    user_id = st.session_state['user']['id']
    user_email = st.session_state['user']['email'].replace("@", "_").replace(".", "_")
except (KeyError, TypeError):
    st.error("Session error: User information is incomplete. Please log in again.")
    st.session_state['logged_in'] = False
    st.session_state['user'] = None
    st.experimental_rerun()

# Sidebar Menu
menu = ["Add Job", "View Jobs", "Find Jobs", "Stats Dashboard"]
choice = st.sidebar.selectbox("📂 Menu", menu)

# Folder setup
RESUME_DIR = "resume_uploads"
COVER_DIR = "cover_letters"
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(COVER_DIR, exist_ok=True)

# --- Add Job ---
if choice == "Add Job":
    st.subheader("➕ Add New Job Application")

    with st.form("job_form"):
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("🏢 Company Name")
            position = st.text_input("💼 Position Title")
        with col2:
            status = st.selectbox("📌 Application Status", ["Applied", "Interview", "Rejected", "Offer", "Accepted"])
            date_applied = st.date_input("📅 Date Applied", datetime.date.today())
            deadline = st.date_input("📆 Application Deadline", datetime.date.today())

        resume = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        cover_letter = st.file_uploader("📝 Upload Cover Letter (PDF/DOCX)", type=["pdf", "docx"])
        submit = st.form_submit_button("Add Job")

        if submit:
            if company and position:
                resume_path = ""
                if resume is not None:
                    safe_resume_name = f"{user_email}_resume_{resume.name}"
                    resume_path = os.path.join(RESUME_DIR, safe_resume_name)
                    with open(resume_path, "wb") as f:
                        f.write(resume.getbuffer())

                cover_letter_path = ""
                if cover_letter is not None:
                    safe_cover_name = f"{user_email}_cover_{cover_letter.name}"
                    cover_letter_path = os.path.join(COVER_DIR, safe_cover_name)
                    with open(cover_letter_path, "wb") as f:
                        f.write(cover_letter.getbuffer())

                add_job(user_id, company, position, status, str(date_applied), str(deadline), resume_path, cover_letter_path)
                st.success(f"✅ Added job application for {position} at {company}")
            else:
                st.warning("⚠️ Please fill in all required fields.")

# --- View Jobs ---
elif choice == "View Jobs":
    st.subheader("📋 All Job Applications")
    data = view_jobs(user_id)
    if data:
        filter_company = st.text_input("🔎 Search by Company")
        filter_status = st.selectbox("📁 Filter by Status", ["All", "Applied", "Interview", "Offer", "Rejected", "Accepted"])
        start_date, end_date = st.date_input("📅 Filter by Date Range", [datetime.date(2024, 1, 1), datetime.date.today()])

        filtered = [row for row in data if (filter_company.lower() in row[2].lower()) and
                    (filter_status == "All" or row[4] == filter_status) and
                    (start_date <= datetime.date.fromisoformat(row[5]) <= end_date)]

        df_full = pd.DataFrame(filtered, columns=["ID", "User ID", "Company", "Position", "Status", "Date Applied", "Deadline", "Resume", "Cover Letter"])
        df_display = df_full.drop(columns=["User ID", "Resume", "Cover Letter"])
        st.dataframe(df_display, use_container_width=True)

        for i, row in df_full.iterrows():
            with st.expander(f"📌 {row['Company']} - {row['Position']}"):
                st.markdown(f"**Status:** {row['Status']}")
                new_status = st.selectbox("Update Status", ["Applied", "Interview", "Offer", "Rejected", "Accepted"], index=["Applied", "Interview", "Offer", "Rejected", "Accepted"].index(row['Status']), key=f"status_{i}")
                if new_status != row['Status']:
                    update_job_status(row['ID'], new_status)
                    send_email(user_email, row['Company'], row['Position'], new_status)
                    st.success("📧 Status updated and email sent!")
                    st.experimental_rerun()

                if os.path.exists(row['Resume']):
                    with open(row['Resume'], "rb") as f:
                        st.download_button(
                            label="📄 Download Resume",
                            data=f,
                            file_name=os.path.basename(row['Resume']),
                            key=f"download_resume_{row['ID']}"
                 )

                if os.path.exists(row['Cover Letter']):
                    with open(row['Cover Letter'], "rb") as f:
                        st.download_button(
                            label="📝 Download Cover Letter",
                            data=f,
                            file_name=os.path.basename(row['Cover Letter']),
                            key=f"download_cover_{row['ID']}"
                        )
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="job_applications.csv", mime="text/csv")
    else:
        st.info("No job applications found.")

# --- Find Jobs ---
elif choice == "Find Jobs":
    st.subheader("🌐 Find Internships/Jobs on the Internet")
    with st.form("search_form"):
        keyword = st.text_input("🔍 Job Title or Company")
        location = st.text_input("📍 Location (optional)")
        skills = st.text_input("💡 Skills (comma-separated, optional)")
        submit = st.form_submit_button("Search")

        if submit:
            with st.spinner("Searching jobs online..."):
                jobs = search_jobs(keyword, location, skills)
                if jobs:
                    for job in jobs:
                        with st.expander(f"{job['job_title']} at {job['employer_name']}"):
                            st.markdown(f"**Location:** {job.get('job_city', '')}")
                            st.markdown(f"**Employment Type:** {job.get('job_employment_type', '')}")
                            st.markdown(f"**Posted:** {job.get('job_posted_at_datetime_utc', '')}")
                            st.markdown(f"**Apply Link:** [Click here]({job['job_apply_link']})")
                else:
                    st.warning("No jobs found. Try adjusting your search.")

# --- Stats Dashboard ---
elif choice == "Stats Dashboard":
    st.subheader("📊 Job Application Stats")
    data = view_jobs(user_id)
    if data:
        df = pd.DataFrame(data, columns=["ID", "User ID", "Company", "Position", "Status", "Date Applied", "Deadline", "Resume", "Cover Letter"])

        # Pie chart
        pie_chart = px.pie(df, names="Status", title="Application Status Distribution")
        st.plotly_chart(pie_chart, use_container_width=True)

        # Bar chart by month
        df["Month"] = pd.to_datetime(df["Date Applied"]).dt.to_period("M").astype(str)
        bar_chart = px.bar(df.groupby("Month").size().reset_index(name='Applications'),
                           x="Month", y="Applications", title="Applications per Month")
        st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.info("No job applications to show stats.")


def load_static_assets():
    css_file_path = "static/css/style.css"
    if os.path.exists(css_file_path):
        with open(css_file_path) as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ CSS file not found. UI may look plain.")

    js_file_path = "static/JS/script.js"
    if os.path.exists(js_file_path):
        with open(js_file_path) as js_file:
            st.markdown(f"<script>{js_file.read()}</script>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ JS file not found. UI may not function properly.")