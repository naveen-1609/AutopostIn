# ✅ auth/linkedin_oauth.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
import os
from utils.firebase import save_user
from dotenv import load_dotenv
import traceback
load_dotenv()

linkedin_router = APIRouter()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
EXISTING_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

@linkedin_router.get("/auth/linkedin/login")
def login_linkedin():
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile%20email%20w_member_social"
    )
    return RedirectResponse(auth_url)

@linkedin_router.get("/callback")
async def linkedin_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Code not found in callback")
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_res = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to get access token")

            # Step 2: Get userinfo using access token
            userinfo_res = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo = userinfo_res.json()
            print("🧑‍💼 Userinfo:", userinfo)

            sub = userinfo.get("sub")
            name = userinfo.get("name", "LinkedIn User")

            if not sub:
                raise HTTPException(status_code=400, detail="User ID (sub) not found in userinfo")

            urn = f"urn:li:person:{sub}"

            # Step 3: Save to Firestore
            save_user(sub, {
                "access_token": access_token,
                "name": name,
                "urn": urn
            })

            # Step 4: Redirect to Streamlit with ID
            return RedirectResponse(url=f"https://autopostin.onrender.com?user_id={sub}")

    except Exception as e:
        print("❌ Callback error:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))