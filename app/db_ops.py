from app.database import get_db, PRReview
from datetime import datetime, timedelta
from sqlalchemy import func

def save_review(repo: str, pr_number: int, pr_title: str, review: dict):
    db = get_db()
    if not db:
        return
    try:
        pr_review = PRReview(
            repo=repo,
            pr_number=pr_number,
            pr_title=pr_title,
            verdict=review.get("verdict", "COMMENT"),
            confidence=review.get("confidence", 0.0),
            issues_count=len(review.get("issues", [])),
            suggestions_count=len(review.get("suggestions", []))
        )
        db.add(pr_review)
        db.commit()
        print(f"Saved review for PR #{pr_number} to database")
    except Exception as e:
        print(f"Error saving review: {e}")
        db.rollback()
    finally:
        db.close()

def get_stats(repo: str = None):
    db = get_db()
    if not db:
        return None
    try:
        query = db.query(PRReview)
        if repo:
            query = query.filter(PRReview.repo == repo)

        total = query.count()
        if total == 0:
            return {
                "prs_reviewed": 0,
                "avg_confidence": 0,
                "total_issues": 0,
                "recent_reviews": []
            }

        avg_conf = db.query(func.avg(PRReview.confidence)).scalar() or 0
        total_issues = db.query(func.sum(PRReview.issues_count)).scalar() or 0

        recent = query.order_by(PRReview.created_at.desc()).limit(5).all()
        recent_reviews = [
            {
                "pr_number": r.pr_number,
                "pr_title": r.pr_title,
                "verdict": r.verdict,
                "confidence": round(r.confidence * 100),
                "created_at": r.created_at.isoformat()
            }
            for r in recent
        ]

        weekly_confidence = []
        for i in range(5, 0, -1):
            week_start = datetime.utcnow() - timedelta(weeks=i)
            week_end = datetime.utcnow() - timedelta(weeks=i-1)
            week_avg = db.query(func.avg(PRReview.confidence)).filter(
                PRReview.created_at >= week_start,
                PRReview.created_at < week_end
            ).scalar()
            weekly_confidence.append({
                "week": f"W{6-i}",
                "confidence": round((week_avg or 0) * 100)
            })

        return {
            "prs_reviewed": total,
            "avg_confidence": round(avg_conf * 100),
            "total_issues": int(total_issues),
            "recent_reviews": recent_reviews,
            "weekly_confidence": weekly_confidence
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None
    finally:
        db.close()