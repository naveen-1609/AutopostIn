import streamlit as st
import requests

API_BASE = "https://autopostin.onrender.com"

st.set_page_config(page_title="AutopostIn Dashboard", layout="centered")

# --------- Session Setup ----------
query_params = st.query_params
user_id = query_params.get("user_id", [None])[0]
name = query_params.get("name", [""])[0]

if user_id and "user_id" not in st.session_state:
    st.session_state.user_id = user_id
    st.session_state.name = name
    st.query_params.clear()
    st.rerun()

if "user_id" not in st.session_state or not st.session_state.user_id:
    st.title("AutopostIn")
    st.markdown("### Login using LinkedIn")
    st.markdown("[Login with LinkedIn](https://autopostin.onrender.com/auth/linkedin/login)")
    st.stop()

# -------- Sidebar Navigation --------
st.sidebar.title("📌 AutopostIn")
page = st.sidebar.radio("Navigate", ["📝 New Job", "📄 Scheduled Jobs"])

# Place Logout button at the bottom
st.sidebar.markdown(
    """
    <style>
    .logout-button { position: fixed; bottom: 20px; width: 85%; }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("🔓 Logout"):
    st.session_state.clear()
    st.switch_page("https://autopostin.onrender.com/auth/linkedin/login")

if page == "📝 New Job":
    # -------- New Job Page --------
    st.title("📝 Schedule a Job")
    st.success(f"✅ Logged in as: {st.session_state.name}")

    with st.form("create_job"):
        topic = st.text_input("Topic", value="Artificial Intelligence")
        job_type = st.selectbox("Post Type", ["daily", "one time", "weekly", "roadmap", "day series"])
        days = None
        if job_type in ["daily", "day series", "roadmap"]:
            days = st.number_input("How many days (if applicable)?", min_value=1, max_value=30, value=5)

        submitted = st.form_submit_button("Generate & Schedule Posts")

        if submitted:
            gen_payload = {"topic": topic, "method": job_type}
            if days:
                gen_payload["days"] = days

            gen_response = requests.post(f"{API_BASE}/generate", json=gen_payload)
            st.write("🪪 Current User ID:", st.session_state.get("user_id"))
            if gen_response.status_code == 200:
                posts = gen_response.json()["posts"]
                for post in posts:
                    post["status"] = "scheduled"

                st.success("Generated posts preview:")
                for post in posts:
                    st.markdown(f"**Day {post.get('day', post.get('week', 1))}**")
                    st.write(post["content"])
                    if "scheduled_time" in post:
                        st.caption(f"🕒 Scheduled for: {post['scheduled_time']}")

                job_payload = {
                    "user_id": st.session_state.user_id,
                    "topic": topic,
                    "type": job_type,
                    "days": days,
                    "posts": posts
                }
                job_response = requests.post(f"{API_BASE}/create", json=job_payload)
                if job_response.status_code == 200:
                    st.success("✅ Job created and posts scheduled.")
                else:
                    st.error("❌ Failed to create job.")
            else:
                st.error("❌ Post generation failed.")

elif page == "📄 Scheduled Jobs":
    # -------- Scheduled Jobs Page --------
    st.title("📄 Scheduled Jobs")
    jobs_response = requests.get(f"{API_BASE}/jobs/{st.session_state.user_id}")

    if jobs_response.status_code == 200:
        jobs = jobs_response.json()
        if jobs:
            for index, job in enumerate(jobs):
                st.subheader(f"🔹 {job.get('topic')} ({job.get('type')})")
                st.write(f"🕒 Created: {job.get('created_at', 'N/A')}")
                st.write(f"📌 Status: {job.get('status', 'unknown')}")
                st.write(f"✍️ Posts Scheduled: {len(job.get('posts', []) or [])}")

                next_scheduled = next((p.get("scheduled_time") for p in job.get("posts", []) if p.get("status") == "scheduled"), None)
                if next_scheduled:
                    st.info(f"⏰ Next post scheduled at: {next_scheduled}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🗑️ Delete", key=f"delete_{index}"):
                        requests.delete(f"{API_BASE}/jobs/delete/{job.get('id')}")
                        st.rerun()
                with col2:
                    if job.get("status") == "paused":
                        if st.button(f"▶️ Resume", key=f"resume_{index}"):
                            requests.post(f"{API_BASE}/jobs/resume/{job.get('id')}")
                            st.rerun()
                    else:
                        if st.button(f"⏹️ Stop", key=f"stop_{index}"):
                            requests.post(f"{API_BASE}/jobs/stop/{job.get('id')}")
                            st.rerun()
                with col3:
                    if st.button(f"⏸️ Pause 1 Cycle", key=f"pause_{index}"):
                        requests.post(f"{API_BASE}/jobs/pause/{job.get('id')}")
                        st.rerun()
                st.markdown("---")
        else:
            st.info("ℹ️ No jobs scheduled yet.")
    else:
        st.error("❌ Failed to fetch jobs from backend.")
