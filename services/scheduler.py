from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import ConflictingIdError
from utils.firebase import get_due_posts, update_post_status
from services.linkedin_api import post_to_linkedin
import asyncio
from datetime import datetime
import pytz
import logging

scheduler = BackgroundScheduler(timezone="America/New_York")
scheduler_started = False  # Global flag to avoid reinitialization


def schedule_job_at_exact_time(job_id, post_index, post):
    """
    Schedules a single job to be posted at the exact scheduled time.
    """
    try:
        scheduled_time = datetime.fromisoformat(post["scheduled_time"])
        job_uid = f"{job_id}-{post_index}"
        if not scheduler.get_job(job_uid):
            scheduler.add_job(
                func=post_linkedin_job,
                trigger=DateTrigger(run_date=scheduled_time),
                args=[job_id, post_index, post],
                id=job_uid,
                misfire_grace_time=120  # 2-minute grace period
            )
    except Exception as e:
        logging.error(f"❌ Failed to schedule job {job_id}-{post_index}: {e}")


def post_linkedin_job(job_id, post_index, post):
    """
    Executes the actual posting to LinkedIn and updates post status.
    """
    try:
        post_text = post["content"]
        access_token = post["access_token"]
        urn = post["urn"]
        if "member:" in urn:
            urn = urn.replace("member:", "person:")  # LinkedIn expects "person:"

        logging.info(f"📢 Posting job {job_id} - post {post_index}")
        status_code, _ = asyncio.run(post_to_linkedin(access_token, urn, post_text))
        update_post_status(job_id, post_index, "posted" if status_code == 201 else "failed")
    except Exception as e:
        logging.error(f"❌ Error posting job {job_id}: {e}")


def schedule_all_upcoming_posts():
    """
    Checks Firestore for all upcoming jobs and schedules any unscheduled ones.
    """
    try:
        due_posts = get_due_posts(include_future=True)
        for job_id, post_index, post in due_posts:
            job_uid = f"{job_id}-{post_index}"
            if not scheduler.get_job(job_uid):
                schedule_job_at_exact_time(job_id, post_index, post)
    except Exception as e:
        logging.error(f"❌ Failed to check and schedule upcoming posts: {e}")


def start_scheduler():
    """
    Starts the APScheduler and schedules both initial and future jobs.
    """
    global scheduler_started
    if scheduler_started:
        print("⚠️ Scheduler already started. Skipping...")
        return

    print("✅ Scheduling all upcoming posts...")
    schedule_all_upcoming_posts()

    # 🔁 Check for new jobs every 60 seconds
    scheduler.add_job(
        func=schedule_all_upcoming_posts,
        trigger=IntervalTrigger(seconds=60),
        id="poll_new_jobs"
    )

    scheduler.start()
    scheduler_started = True
    print("✅ APScheduler started.")
