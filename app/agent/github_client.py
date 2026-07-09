import os
import jwt
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")

def generate_jwt() -> str:
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID
    }

    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_token(installation_id: int) -> str:
    token = generate_jwt()

    response = httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
    )
    return response.json()["token"]

def get_pr_diff(repo_full_name: str, pr_number: int, token: str) -> str:
    response = httpx.get(
        f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.diff"
        }
    )
    return response.text

def format_review(review: dict) -> str:
    verdict = review.get("verdict", "COMMENT")
    confidence = review.get("confidence", 0.0)

    verdict_emoji = {
        "APPROVE": "✅",
        "REQUEST_CHANGES": "❌",
        "COMMENT": "💬"
    }.get(verdict, "💬")

    confidence_bar = int(confidence * 10)
    confidence_display = "█" * confidence_bar + "░" * (10 - confidence_bar)

    issues = review.get("issues", [])
    suggestions = review.get("suggestions", [])

    issues_text = "\n".join(f"- {i}" for i in issues) if issues else "No issues found ✓"
    suggestions_text = "\n".join(f"- {s}" for s in suggestions) if suggestions else "No suggestions"

    return f"""## 🤖 CodeSense AI Review

**Verdict:** {verdict_emoji} {verdict}
**Confidence:** `{confidence_display}` {int(confidence * 100)}%

### 📋 Summary
{review.get("summary", "N/A")}

### 🔄 Consistency
{review.get("consistency", "N/A")}

### 🐛 Issues
{issues_text}

### 💡 Suggestions
{suggestions_text}

---
*Powered by CodeSense + Llama 3.3 70b*"""

def post_review_comment(repo_full_name: str, pr_number: int, review: dict, token: str):
    body = format_review(review)

    httpx.post(
        f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        json={"body": body}
    )