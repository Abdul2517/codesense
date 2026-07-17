from fastapi import HTTPException
from typing import Optional


def validate_pr_payload(payload: dict) -> tuple[str, int, str, int]:
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {}).get("full_name", "")
    installation_id = payload.get("installation", {}).get("id", 0)
    pr_number = pr.get("number", 0)
    pr_title = pr.get("title", "")

    if not repo:
        raise HTTPException(status_code=400, detail="Missing repository info")
    if not pr_number:
        raise HTTPException(status_code=400, detail="Missing PR number")
    if not installation_id:
        raise HTTPException(status_code=400, detail="Missing installation ID")

    return repo, pr_number, pr_title, installation_id


def safe_truncate(text: str, max_chars: int = 10000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... (truncated {len(text) - max_chars} chars)"


def is_valid_diff(diff: str) -> bool:
    if not diff or len(diff.strip()) == 0:
        return False
    if len(diff) < 10:
        return False
    return True