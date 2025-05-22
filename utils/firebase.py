import os
import pytz
from dotenv import load_dotenv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

load_dotenv()
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    initialize_app(cred)

db = firestore.client()

db = firestore.client()

def get_user_by_id(user_id):
    return db.collection("users").document(user_id).get().to_dict()

def save_user(user_id, data):
    db.collection("users").document(user_id).set(data)

def save_job(user_id, job_data):
    return db.collection("jobs").add({**job_data, "user_id": user_id})

def delete_job(job_id):
    db.collection("jobs").document(job_id).delete()

def get_jobs_by_user(user_id):
    return db.collection("jobs").where("user_id", "==", user_id).stream()

def update_job_status(job_id, new_status):
    job_ref = db.collection("jobs").document(job_id)
    job = job_ref.get().to_dict()
    if job:
        if new_status == "pause_one":
            for post in job.get("posts", []):
                if post.get("status") == "scheduled":
                    post["status"] = "skipped"
                    break
        else:
            job["status"] = new_status
        job_ref.set(job)

def update_post_status(job_id, post_index, status):
    job_ref = db.collection("jobs").document(job_id)
    job = job_ref.get().to_dict()
    if job and "posts" in job:
        job["posts"][post_index]["status"] = status
        job_ref.set(job)

def get_due_posts(include_future=False):
    jobs = db.collection("jobs").stream()
    due_posts = []
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    for job in jobs:
        job_data = job.to_dict()
        for idx, post in enumerate(job_data.get("posts", [])):
            scheduled_time_str = post.get("scheduled_time")
            if scheduled_time_str and post.get("status") == "scheduled":
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
                if include_future or scheduled_time <= now:
                    post["access_token"] = job_data.get("access_token")
                    post["urn"] = job_data.get("urn")
                    due_posts.append((job.id, idx, post))
    return due_posts