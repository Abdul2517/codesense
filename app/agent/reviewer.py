import os
from groq import Groq
from dotenv import load_dotenv
from app.knowledge.context import get_codebase_context

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(diff: str, pr_title: str) -> str:
    codebase_context = get_codebase_context(".")

    prompt = f"""You are an expert code reviewer who knows this codebase well. Review the pull request using both the existing codebase context and the new changes.

## Existing Codebase
{codebase_context}

## Pull Request: {pr_title}

## Code Changes (diff)
{diff}

Provide a structured review with:
1. **Summary** - What this PR does
2. **Consistency** - Does it follow patterns already in the codebase?
3. **Issues** - Any bugs, security issues, or problems
4. **Suggestions** - Specific improvements referencing existing code where relevant
5. **Verdict** - APPROVE, REQUEST CHANGES, or COMMENT

Be specific. Reference actual file names and function names from the codebase when relevant."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.3
    )

    return response.choices[0].message.content