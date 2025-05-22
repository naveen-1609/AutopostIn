from fastapi import FastAPI
from routes.jobs import jobs_router
from routes.posts import posts_router
from auth.linkedin_oauth import linkedin_router
from services.scheduler import start_scheduler
from fastapi.responses import HTMLResponse

app = FastAPI()

app.include_router(linkedin_router)
app.include_router(posts_router)
app.include_router(jobs_router, prefix="/jobs")
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Welcome to AutopostIn 🚀</h2>
    <a href='/auth/linkedin/login'>Login with LinkedIn</a>
    """

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(user_id: str):
    return f"""
    <h2>Welcome, User: {user_id}</h2>
    <p>Use Postman or UI to generate posts or create scheduled jobs.</p>
    """

start_scheduler()