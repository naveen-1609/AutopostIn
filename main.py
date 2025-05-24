from fastapi import FastAPI
from routes.jobs import jobs_router
from routes.posts import posts_router
from auth.linkedin_oauth import linkedin_router
from services.scheduler import start_scheduler
from fastapi.responses import HTMLResponse

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Add this CORS setup BEFORE include_router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(linkedin_router)
app.include_router(posts_router)
app.include_router(jobs_router)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Welcome to AutopostIn</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f6f8;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background-color: white;
                padding: 40px 60px;
                border-radius: 10px;
                box-shadow: 0 0 12px rgba(0,0,0,0.1);
            }
            .btn {
                background-color: #0077b5;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                display: inline-block;
                margin-top: 20px;
                transition: background-color 0.3s ease;
            }
            .btn:hover {
                background-color: #005983;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Welcome to <span style="color:#0077b5;">AutopostIn</span></h1>
            <p>Automate your daily LinkedIn content effortlessly.</p>
            <a href="/auth/linkedin/login" class="btn">🔐 Login with LinkedIn</a>
        </div>
    </body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(user_id: str):
    return f"""
    <h2>Welcome, User: {user_id}</h2>
    <p>Use Postman or UI to generate posts or create scheduled jobs.</p>
    """

start_scheduler()