from typing import Optional


def parse_diff_stats(diff: str) -> dict:
    """Parse a git diff and return statistics."""
    lines = diff.split("\n")
    additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    files_changed = sum(1 for l in lines if l.startswith("diff --git"))

    return {
        "additions": additions,
        "deletions": deletions,
        "files_changed": files_changed,
        "net_change": additions - deletions
    }


def is_large_pr(diff: str, threshold: int = 500) -> bool:
    stats = parse_diff_stats(diff)
    total = stats["additions"] + stats["deletions"]
    return total > threshold


def extract_changed_files(diff: str) -> list:
    files = []
    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" ")
            if len(parts) >= 4:
                file_path = parts[3].lstrip("b/")
                files.append(file_path)
    return files


def get_pr_size_label(diff: str) -> str:
    stats = parse_diff_stats(diff)
    total = stats["additions"] + stats["deletions"]
    if total < 10:
        return "XS"
    elif total < 50:
        return "S"
    elif total < 200:
        return "M"
    elif total < 500:
        return "L"
    else:
        return "XL"


def truncate_diff(diff: str, max_lines: int = 200) -> str:
    lines = diff.split("\n")
    if len(lines) <= max_lines:
        return diff
    truncated = lines[:max_lines]
    truncated.append(f"\n... diff truncated ({len(lines) - max_lines} lines removed)")
    return "\n".join(truncated)