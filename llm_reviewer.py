import os
import sys
import requests

# Configuration
GITLAB_API_URL = os.environ.get("CI_API_V4_URL", "https://gitlab.com/api/v4")
PROJECT_ID = os.environ.get("CI_PROJECT_ID")
MR_IID = os.environ.get("CI_MERGE_REQUEST_IID")

GITLAB_PRIVATE_TOKEN = os.environ.get("GITLAB_PRIVATE_TOKEN")
CI_JOB_TOKEN = os.environ.get("CI_JOB_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

LLM_MODEL = os.environ.get("LLM_MODEL", "anthropic/claude-3.5-sonnet")

if not all([PROJECT_ID, MR_IID, OPENROUTER_API_KEY]) or not (
    GITLAB_PRIVATE_TOKEN or CI_JOB_TOKEN
):
    print("Missing required environment variables.")
    print(
        f"Debug: PROJECT_ID={bool(PROJECT_ID)}, MR_IID={bool(MR_IID)}, OPENROUTER_API_KEY={bool(OPENROUTER_API_KEY)}"
    )
    print(
        f"Debug: GITLAB_PRIVATE_TOKEN={bool(GITLAB_PRIVATE_TOKEN)}, CI_JOB_TOKEN={bool(CI_JOB_TOKEN)}"
    )
    sys.exit(1)


def get_gitlab_headers():
    if GITLAB_PRIVATE_TOKEN:
        return {"PRIVATE-TOKEN": GITLAB_PRIVATE_TOKEN}
    else:
        return {"JOB-TOKEN": CI_JOB_TOKEN}


def get_mr_changes():
    """Fetch the changes in the Merge Request."""
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MR_IID}/changes"
    headers = get_gitlab_headers()
    print(f"Fetching changes from: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def analyze_diff(changes):
    """Send the diff to OpenRouter for analysis."""
    diffs = []
    file_list = []

    for change in changes.get("changes", []):
        new_path = change["new_path"]
        file_list.append(new_path)
        # Skip deleted files or binary files if necessary
        if change.get("deleted_file"):
            continue

        diff_content = change.get("diff", "")
        diffs.append(f"### File: {new_path}\n```diff\n{diff_content}\n```")

    diff_text = "\n\n".join(diffs)
    files_summary = ", ".join(file_list)

    # Detect languages based on file extensions
    extensions = {os.path.splitext(f)[1] for f in file_list if os.path.splitext(f)[1]}
    
    # Basic mapping of extensions to languages (can be expanded)
    ext_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React (JS)",
        ".tsx": "React (TS)",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".php": "PHP",
        ".rb": "Ruby",
        ".c": "C",
        ".cpp": "C++",
        ".cs": "C#",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sql": "SQL",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".json": "JSON",
        ".md": "Markdown",
        ".sh": "Shell Script",
        ".dockerfile": "Dockerfile",
    }
    
    languages = sorted({ext_map.get(ext, ext) for ext in extensions})
    languages_str = ", ".join(languages) if languages else "Unknown"
    project_name = os.environ.get("CI_PROJECT_NAME", "the project")

    system_prompt = f"""You are a senior software engineer and code reviewer for the project '{project_name}'.
    
    Your task is to review the following Merge Request changes.
    
    Project Context:
    - Languages detected in this MR: {languages_str}
    
    Review Guidelines:
    1. Analyze the code for bugs, logical errors, and edge cases.
    2. Check for security vulnerabilities (e.g., injection, sensitive data exposure, auth issues).
    3. Ensure adherence to best practices and coding standards for the detected languages.
    4. Suggest performance improvements where obvious.
    5. Check for readability, maintainability, and proper error handling.
    6. Be concise, constructive, and polite.
    
    The files modified in this MR are: {files_summary}
    
    Please provide your review in Markdown format. If the code looks good, say so, but briefly mention what was verified.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please review these changes:\n\n{diff_text}"},
    ]

    payload = {"model": LLM_MODEL, "messages": messages, "temperature": 0.2}

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("CI_PROJECT_URL", "https://gitlab.com"),
        "X-Title": "GitLab CI Code Review",
    }

    print(f"Sending request to OpenRouter (Model: {LLM_MODEL})...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers
    )

    if response.status_code != 200:
        print(f"OpenRouter API Error: {response.text}")
        response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]


def post_comment(comment):
    """Post the review as a comment on the Merge Request."""
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MR_IID}/notes"
    headers = get_gitlab_headers()

    # Add a header to the comment
    full_body = f"## 🤖 AI Code Review (Model: {LLM_MODEL})\n\n{comment}"

    payload = {"body": full_body}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print("Comment posted successfully to GitLab.")


def main():
    print(f"Starting AI Code Review for MR !{MR_IID}...")
    try:
        changes = get_mr_changes()
        if not changes.get("changes"):
            print("No changes found in this MR.")
            return

        review = analyze_diff(changes)
        post_comment(review)

    except Exception as e:
        print(f"An error occurred: {e}")
        # We don't want to fail the pipeline if the AI review fails, just log it.
        sys.exit(0)


if __name__ == "__main__":
    main()
