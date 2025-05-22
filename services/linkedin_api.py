import httpx
import logging

async def post_to_linkedin(access_token: str, urn: str, text: str):
    clean_text = text.strip()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    payload = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": clean_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post("https://api.linkedin.com/v2/ugcPosts", json=payload, headers=headers)
            if res.status_code == 201:
                return 201, "✅ Post created successfully."
            else:
                logging.warning(f"⚠️ Failed to post: {res.status_code} | {res.text}")
                return res.status_code, res.text
        except Exception as e:
            logging.error(f"❌ Exception during LinkedIn post: {e}")
            return 500, str(e)