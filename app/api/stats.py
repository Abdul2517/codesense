from fastapi import APIRouter
from app.knowledge.vector_store import get_pr_count
from app.knowledge.rule_extractor import load_existing_rules
from app.db_ops import get_stats

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/")
def get_all_stats():
    pr_count = get_pr_count()
    rules = load_existing_rules()
    db_stats = get_stats()

    return {
        "prs_reviewed": db_stats["prs_reviewed"] if db_stats else pr_count,
        "avg_confidence": db_stats["avg_confidence"] if db_stats else 0,
        "total_issues": db_stats["total_issues"] if db_stats else 0,
        "rules_extracted": len(rules),
        "rules": rules,
        "recent_reviews": db_stats["recent_reviews"] if db_stats else [],
        "weekly_confidence": db_stats["weekly_confidence"] if db_stats else [],
        "status": "online"
    }