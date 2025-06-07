import os
import sys
import subprocess
from github import Github

def pr_exists(g, repo_name, branch):
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch}")
    return pulls.totalCount > 0

def run():
    # Set safe directory to avoid git warnings in GitHub Actions runner
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", os.getcwd()], check=True)

    # Required environment variables
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
    BOT_NAME = os.environ.get("BOT_NAME", "code-comment-bot")
    BOT_EMAIL = os.environ.get("BOT_EMAIL", "bot@your-org.com")
    BRANCH_NAME = os.environ.get("BOT_BRANCH", "auto/comment-update")
    PR_TITLE = os.environ.get("PR_TITLE", "🤖 Add Code Comments")
    PR_BODY = os.environ.get("PR_BODY", "This PR includes auto-generated code comments.")

    config_arg = sys.argv[1] if len(sys.argv) > 1 else None
    src_arg = sys.argv[2] if len(sys.argv) > 2 else "."

    # Initialize Github API client
    gh = Github(GITHUB_TOKEN)
    if pr_exists(gh, GITHUB_REPOSITORY, BRANCH_NAME):
        print("✅ PR already exists. Skipping PR creation.")
    # Setup git user info for commits
    subprocess.run(["git", "config", "user.name", BOT_NAME], check=True)
    subprocess.run(["git", "config", "user.email", BOT_EMAIL], check=True)

    # Run your bot CLI or whatever tool does the code commenting
    subprocess.run([
        "python", "-m", "bot.cli",
        "--config", config_arg,
        "--src", src_arg
    ], check=True)

    # Create / reset branch
    subprocess.run(["git", "checkout", "-B", BRANCH_NAME], check=True)

    # Stage all changes
    subprocess.run(["git", "add", "-A"], check=True)

    # Commit changes, allow empty commits if no changes to avoid errors
    try:
        subprocess.run(["git", "commit", "-m", "🤖 Auto-commented code"], check=True)
    except subprocess.CalledProcessError:
        print("No changes to commit.")

    # Push changes using the token in remote URL for authentication
    token_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"
    print(f"Pushing to remote using token URL: {token_url}")
    

    # Force push to the branch
    subprocess.run(["git", "push", token_url, f"{BRANCH_NAME}:{BRANCH_NAME}", "--force"], check=True)

    # Create PR 
    repo = gh.get_repo(GITHUB_REPOSITORY)
    pr = repo.create_pull(
        title=PR_TITLE,
        body=PR_BODY,
        head=BRANCH_NAME,
        base="main"
    )
    print(f"✅ Pull request created: {pr.html_url}")

if __name__ == "__main__":
    run()
