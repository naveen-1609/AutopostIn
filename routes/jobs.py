from fastapi import APIRouter, HTTPException
from models.schema import JobRequest
from utils.firebase import (
    save_job,
    get_user_by_id,
    delete_job,
    update_job_status,
    get_jobs_by_user
)
from firebase_admin import firestore
from datetime import datetime, timedelta
import pytz

jobs_router = APIRouter()

@jobs_router.post("/create")
def create_job(job: JobRequest):
    user = get_user_by_id(job.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_york_tz = pytz.timezone("America/New_York")
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(new_york_tz)
    job_posts = []

    for i, post in enumerate(job.posts):
        post_time = now
        if job.type == "one time":
            post_time += timedelta(minutes=5)
        elif job.type == "daily":
            post_time += timedelta(days=i)
        elif job.type == "weekly":
            post_time += timedelta(weeks=i)
        elif job.type == "day series":
            post_time += timedelta(days=i)
        elif job.type == "roadmap":
            post_time += timedelta(days=i * 2)

        post["scheduled_time"] = post_time.isoformat()
        post["status"] = "scheduled"
        job_posts.append(post)

    job_data = {
        "topic": job.topic,
        "type": job.type,
        "created_at": firestore.SERVER_TIMESTAMP,
        "status": "active",
        "access_token": user.get("access_token"),
        "urn": user.get("urn"),
        "posts": job_posts,
        "user_id": job.user_id
    }

    save_job(job.user_id, job_data)
    return {"message": "Job created"}

@jobs_router.get("/jobs/{user_id}")
def list_jobs(user_id: str):
    jobs = get_jobs_by_user(user_id)
    return [job.to_dict() | {"id": job.id} for job in jobs]

@jobs_router.delete("/jobs/delete/{job_id}")
def delete_scheduled_job(job_id: str):
    delete_job(job_id)
    return {"message": "Job deleted"}

@jobs_router.post("/jobs/pause/{job_id}")
def pause_job(job_id: str):
    update_job_status(job_id, "pause_one")
    return {"message": "Job paused for one cycle"}

@jobs_router.post("/jobs/stop/{job_id}")
def stop_job(job_id: str):
    update_job_status(job_id, "stopped")
    return {"message": "Job stopped"}

@jobs_router.post("/jobs/resume/{job_id}")
def resume_job(job_id: str):
    update_job_status(job_id, "active")
    return {"message": "Job resumed"}
