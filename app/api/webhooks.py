import hmac
import hashlib
import os
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from app.agent.reviewer import review_code
from app.agent.github_client import get_installation_token, get_pr_diff, post_review_comment

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["webhook"])

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "codesense123")
REVIEW_TIMEOUT = 60

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

async def process_pr(repo_full_name: str, pr_number: int, pr_title: str, installation_id: int):
    try:
        print(f"Background task started for PR #{pr_number}")
        print(f"Processing PR #{pr_number} — fetching diff...")
        token = get_installation_token(installation_id)
        diff = get_pr_diff(repo_full_name, pr_number, token)

        if not diff or len(diff.strip()) == 0:
            print("No diff found, skipping review")
            return

        print(f"Running AI review on PR #{pr_number}...")

        try:
            review = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, review_code, diff, pr_title
                ),
                timeout=REVIEW_TIMEOUT
            )
        except asyncio.TimeoutError:
            print(f"Review timed out for PR #{pr_number}")
            review = {
                "summary": "Review timed out. The diff may be too large.",
                "consistency": "Unknown",
                "issues": [],
                "suggestions": ["Consider breaking this PR into smaller chunks."],
                "verdict": "COMMENT",
                "confidence": 0.0
            }

        print(f"Posting review comment on PR #{pr_number}...")
        post_review_comment(repo_full_name, pr_number, review, token)
        print(f"✅ Review posted successfully on PR #{pr_number}")

    except Exception as e:
        print(f"❌ Error processing PR #{pr_number}: {e}")
        import traceback
        traceback.print_exc()

@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
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
        installation_id = payload.get("installation", {}).get("id", "")

        print(f"PR #{pr_number} — {action} — {repo_name} — {pr_title}")
        print(f"Installation ID: {installation_id}")

        if action in ["opened", "synchronize"]:
            background_tasks.add_task(
                process_pr, repo_name, pr_number, pr_title, installation_id
            )
            print(f"Background task queued for PR #{pr_number}")
            return {"status": "review started", "pr": pr_number}

    return {"status": "event ignored", "event": event}