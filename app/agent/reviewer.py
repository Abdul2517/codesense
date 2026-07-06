import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(diff: str, pr_title: str) -> str:
    prompt = f"""You are an expert code reviewer. Review the following pull request and provide constructive feedback.

PR Title: {pr_title}

Code Changes (diff):
{diff}

Provide a structured review with:
1. **Summary** - What this PR does
2. **Issues** - Any bugs, security issues, or problems (if none, say so)
3. **Suggestions** - Improvements to code quality, readability, or performance
4. **Verdict** - APPROVE, REQUEST CHANGES, or COMMENT

Be specific, reference line numbers where possible, and keep it concise."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.3
    )

    return response.choices[0].message.content