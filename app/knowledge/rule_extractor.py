import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.knowledge.vector_store import get_similar_prs, get_pr_count

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RULES_FILE = "codesense.yml"

def extract_rules_from_prs(recent_diffs: list) -> list:
    if not recent_diffs:
        return []

    combined = "\n\n---\n\n".join(recent_diffs[:5])

    prompt = f"""You are analyzing merged pull requests to extract coding standards.

Based on these merged PRs, extract 3-5 concrete coding rules this team follows.

Merged PR diffs:
{combined[:8000]}

Respond ONLY with a JSON array of rule strings, nothing else:
["rule 1", "rule 2", "rule 3"]

Rules should be specific and actionable, like:
- "All functions must have type hints"
- "Use httpx for HTTP requests, not requests library"
- "FastAPI routes must include error handling with HTTPException"
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        start = raw.find('[')
        end = raw.rfind(']') + 1
        if start != -1 and end > start:
            rules = json.loads(raw[start:end])
            return rules
    except Exception as e:
        print(f"Rule extraction error: {e}")

    return []

def save_rules_to_yaml(rules: list, repo_name: str):
    existing_rules = load_existing_rules()
    all_rules = list(set(existing_rules + rules))

    content = f"""# CodeSense — auto-extracted coding rules
# Generated from merged PRs in {repo_name}
# Do not edit manually — updated automatically

rules:
"""
    for rule in all_rules:
        content += f"  - \"{rule}\"\n"

    with open(RULES_FILE, "w") as f:
        f.write(content)

    print(f"Saved {len(all_rules)} rules to {RULES_FILE}")
    return all_rules

def load_existing_rules() -> list:
    if not os.path.exists(RULES_FILE):
        return []
    try:
        with open(RULES_FILE, "r") as f:
            content = f.read()
        rules = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith('- "') and line.endswith('"'):
                rules.append(line[3:-1])
        return rules
    except:
        return []

def maybe_extract_rules(repo_name: str):
    count = get_pr_count()
    print(f"Knowledge base has {count} merged PRs")

    if count > 0 and count % 3 == 0:
        print("Triggering rule extraction...")
        recent_diffs = get_similar_prs("coding patterns functions error handling", n_results=5)
        if recent_diffs:
            rules = extract_rules_from_prs(recent_diffs)
            if rules:
                saved = save_rules_to_yaml(rules, repo_name)
                print(f"Extracted {len(saved)} rules")
                return saved
    return []