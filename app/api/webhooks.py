import hmac
import hashlib
import os
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["webhook"])

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "codesense123")

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/github")
async def github_webhook(request: Request):
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    if event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        pr_title = pr.get("title", "")
        pr_number = pr.get("number", "")
        repo_name = payload.get("repository", {}).get("full_name", "")

        print(f"PR #{pr_number} — {action} — {repo_name} — {pr_title}")

        if action in ["opened", "synchronize"]:
            return {"status": "PR received", "pr": pr_number, "action": action}

    return {"status": "event ignored", "event": event}