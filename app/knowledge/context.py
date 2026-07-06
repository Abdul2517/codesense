import os

IGNORED_DIRS = {'.git', 'venv', '__pycache__', '.env', 'node_modules'}
IGNORED_EXTENSIONS = {'.pyc', '.pem', '.zip', '.png', '.jpg', '.exe'}
MAX_FILE_SIZE = 10000  # characters per file
MAX_TOTAL_SIZE = 50000  # total context characters

def get_codebase_context(repo_path: str = ".") -> str:
    context_parts = []
    total_size = 0

    for root, dirs, files in os.walk(repo_path):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in IGNORED_EXTENSIONS:
                continue

            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, repo_path)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if len(content) > MAX_FILE_SIZE:
                    content = content[:MAX_FILE_SIZE] + "\n... (truncated)"

                file_context = f"### {relative_path}\n```\n{content}\n```\n"
                
                if total_size + len(file_context) > MAX_TOTAL_SIZE:
                    break

                context_parts.append(file_context)
                total_size += len(file_context)

            except Exception:
                continue

    return "\n".join(context_parts)