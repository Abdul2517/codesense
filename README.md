# CodeSense

AI-powered GitHub App that reviews pull requests and learns your team's coding standards automatically.

## What it does

CodeSense installs as a GitHub App on your repository. Every time a pull request is opened or updated, it automatically reads the code diff, reads your existing codebase for context, sends everything to Llama 3.3 70b via Groq, and posts a structured review comment with verdict, confidence score, issues, and suggestions.

## Tech Stack

- Backend: FastAPI + Python 3.11
- LLM: Llama 3.3 70b via Groq (free tier)
- GitHub Integration: GitHub App + Webhooks
- Codebase Context: Custom file scanner
- Deployment: Docker + Railway

## Architecture

GitHub PR opened ? GitHub App webhook ? FastAPI server ? Signature verification ? Fetch PR diff ? Scan codebase ? Groq LLM review ? Post comment to PR

## Setup

1. Clone and install dependencies
   git clone https://github.com/Abdul2517/codesense.git
   cd codesense
   pip install -r requirements.txt

2. Copy .env.example to .env and fill in your values

3. Run locally
   uvicorn app.main:app --reload --port 8000

4. Expose with ngrok
   ngrok http 8000

5. Install the GitHub App and point webhook to your ngrok URL

## Environment Variables

- GROQ_API_KEY: Free API key from console.groq.com
- GITHUB_APP_ID: Your GitHub App ID
- GITHUB_PRIVATE_KEY_PATH: Path to downloaded .pem file
- GITHUB_WEBHOOK_SECRET: Secret set in GitHub App settings

## What makes this different

Most AI code review tools just wrap GPT with a generic prompt. CodeSense reads your actual codebase before reviewing, catches inconsistencies with your real patterns, gives a confidence score, handles timeouts gracefully, and returns structured JSON-parsed reviews not raw text dumps.

## Roadmap

- Completed: GitHub App webhook receiver
- Completed: AI code review with Groq
- Completed: Codebase context scanning
- Completed: Confidence scoring
- Coming: Self-learning from merged PRs
- Coming: Rule extraction engine
- Coming: React dashboard
- Coming: Railway deployment

## License

MIT
