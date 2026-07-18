from fastapi import APIRouter
from app.knowledge.vector_store import get_pr_count
from app.knowledge.rule_extractor import load_existing_rules

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_stats():
    pr_count = get_pr_count()
    rules = load_existing_rules()
    
    return {
        "prs_reviewed": pr_count,
        "rules_extracted": len(rules),
        "rules": rules,
        "status": "online"
    }