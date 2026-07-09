import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.knowledge.context import get_codebase_context

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(diff: str, pr_title: str) -> dict:
    codebase_context = get_codebase_context(".")

    prompt = f"""You are an expert code reviewer. Review this pull request and respond ONLY with a JSON object, no other text, no markdown, no code fences.

## Existing Codebase
{codebase_context}

## Pull Request: {pr_title}

## Code Changes
{diff}

Respond with exactly this JSON structure and nothing else:
{{
    "summary": "one paragraph summary of what this PR does",
    "consistency": "does it follow existing codebase patterns? mention specific files",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "verdict": "APPROVE",
    "confidence": 0.87
}}

verdict must be one of: APPROVE, REQUEST_CHANGES, COMMENT
confidence is a float between 0 and 1
Return only the JSON object, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()

        # Find JSON object in response
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {raw}")
        return {
            "summary": "Review completed but response could not be parsed.",
            "consistency": "Unknown",
            "issues": [],
            "suggestions": [],
            "verdict": "COMMENT",
            "confidence": 0.0
        }
    except Exception as e:
        return {
            "summary": f"Review failed: {str(e)}",
            "consistency": "Unknown",
            "issues": [],
            "suggestions": [],
            "verdict": "COMMENT",
            "confidence": 0.0
        }