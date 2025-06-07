import os
import sys
import subprocess
from github import Github
from git import Repo

def pr_exists(g, repo_name, branch):
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch}")
    return pulls.totalCount > 0

def run():
    # Add current dir as safe for git (needed in GitHub Actions sometimes)
    subprocess.run(["git", "config", "--global", "--add", "safe.directory", os.getcwd()], check=True)

    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
    BOT_NAME = os.environ.get("BOT_NAME", "code-comment-bot")
    BOT_EMAIL = os.environ.get("BOT_EMAIL", "bot@your-org.com")
    BRANCH_NAME = os.environ.get("BOT_BRANCH", "auto/comment-update")
    PR_TITLE = os.environ.get("PR_TITLE", "🤖 Add Code Comments")
    PR_BODY = os.environ.get("PR_BODY", "This PR includes auto-generated code comments.")

    config_arg = sys.argv[1] if len(sys.argv) > 1 else None
    src_arg = sys.argv[2] if len(sys.argv) > 2 else "."

    repo = Repo(".")
    repo.config_writer().set_value("user", "name", BOT_NAME).release()
    repo.config_writer().set_value("user", "email", BOT_EMAIL).release()

    gh = Github(GITHUB_TOKEN)

    # Run your bot CLI or whatever your code does to generate/update code
    subprocess.run([
        "python", "-m", "bot.cli",
        "--config", config_arg,
        "--src", src_arg
    ], check=True)

    # Checkout or create the branch to push to
    repo.git.checkout("-B", BRANCH_NAME)

    # Stage all changes
    repo.git.add(A=True)

    # Commit changes
    repo.index.commit("🤖 Auto-commented code")

    # *** CRUCIAL: set remote URL with token BEFORE push ***
    token_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GITHUB_REPOSITORY}.git"
    repo.remote("origin").set_url(token_url)

    print(f"Pushing to remote: {repo.remote('origin').url}")

    # Push branch with force (overwrite branch on remote)
    repo.remote("origin").push(refspec=f"{BRANCH_NAME}:{BRANCH_NAME}", force=True)

    # Check if PR exists, else create it
    if not pr_exists(gh, GITHUB_REPOSITORY, BRANCH_NAME):
        gh_repo = gh.get_repo(GITHUB_REPOSITORY)
        gh_repo.create_pull(
            title=PR_TITLE,
            body=PR_BODY,
            head=BRANCH_NAME,
            base="main"
        )
        print("✅ Pull request created.")
    else:
        print("✅ PR already exists. Skipping PR creation.")

if __name__ == "__main__":
    run()
